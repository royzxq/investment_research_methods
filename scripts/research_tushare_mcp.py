"""Expose read-only Tushare MCP tools used by stock research."""
import asyncio
from contextlib import asynccontextmanager
import logging
import os
from urllib.parse import urlencode

import httpx2
from mcp import ClientSession, types
from mcp.client.streamable_http import streamable_http_client
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server


BASE_URL = 'https://api.tushare.pro/mcp/'
STOCK_TOOLS = frozenset('''
    stock_basic stock_company namechange trade_cal daily daily_basic adj_factor
    income balancesheet cashflow fina_indicator fina_audit fina_mainbz dividend
    forecast express disclosure_date anns_d repurchase stk_seasoned share_float
    top10_holders top10_floatholders stk_holdernumber stk_holdertrade pledge_stat
    hk_basic hk_tradecal hk_daily hk_daily_adj hk_adjfactor hk_income hk_balancesheet
    hk_cashflow hk_fina_indicator hk_hold stk_ah_comparison fx_midrate
    index_basic index_daily index_weight sw_daily etf_basic fund_daily fund_adj
    fund_nav fund_share fund_portfolio etf_share_size report_rc
'''.split())


@asynccontextmanager
async def connect(token):
    url = BASE_URL + '?' + urlencode({'token': token})
    async with asyncio.timeout(15):
        async with httpx2.AsyncClient(timeout=12, follow_redirects=False) as http:
            async with streamable_http_client(url, http_client=http) as streams:
                async with ClientSession(*streams[:2]) as session:
                    await session.initialize()
                    yield session


async def discover_stock_tools(session):
    tools = {}
    params = None
    seen_cursors = set()
    while True:
        page = await session.list_tools(params=params)
        tools.update((tool.name, tool) for tool in page.tools if tool.name in STOCK_TOOLS)
        cursor = page.next_cursor
        if cursor is None:
            return tools
        if cursor in seen_cursors:
            raise ValueError('Tushare MCP repeated a tool discovery cursor')
        seen_cursors.add(cursor)
        params = types.PaginatedRequestParams(cursor=cursor)


def make_server(token):
    async def list_tools(_context, _params):
        if token:
            try:
                async with connect(token) as session:
                    tools = await discover_stock_tools(session)
                    return types.ListToolsResult(tools=list(tools.values()))
            except Exception:
                # Transport errors may include the authenticated URL.
                logging.warning('Tushare MCP tool discovery failed')
        return types.ListToolsResult(tools=[])

    async def call_tool(_context, params):
        if params.name not in STOCK_TOOLS:
            message = 'This interface is outside the stock research tool set.'
        elif not token:
            message = 'TUSHARE_TOKEN is unavailable.'
        else:
            try:
                async with connect(token) as session:
                    if params.name in await discover_stock_tools(session):
                        return await session.call_tool(params.name, params.arguments)
                    message = 'Tushare MCP did not advertise this interface.'
            except Exception:
                message = 'Tushare MCP request failed. Check the parameters or use another source.'
        return types.CallToolResult(isError=True, content=[types.TextContent(type='text', text=message)])

    return Server('tushareMcp', on_list_tools=list_tools, on_call_tool=call_tool)


async def main():
    # The upstream query string carries a credential. Never log HTTP requests.
    logging.getLogger('httpx2').disabled = True
    logging.getLogger('mcp.client.streamable_http').disabled = True
    server = make_server(os.environ.get('TUSHARE_TOKEN'))
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == '__main__':
    asyncio.run(main())
