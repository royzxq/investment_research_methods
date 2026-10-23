"""Opt-in, isolated DSH/CC research trials. Never imports a production dispatcher."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, wait
from contextlib import contextmanager
from datetime import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import signal
import stat
import sys
import threading
import time
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / 'output/audits/investment/2026-10-21/dsh-isolation'
FOLLOWUP_EXPERIMENTS = ROOT / 'output/audits/investment/2026-10-22/dsh-isolation-v2'
SOURCE_RUN = ROOT / 'output/runs/investment/2026-10-21/f42a808980914f5dbc5a42be145492e7'
MATERIALS = SOURCE_RUN / 'execution/SZ-300750/codex/jev/materials'
SCHEMA = 'research-harness-benchmark/v1'
ACCEPTANCE_CONTRACT = 'stock-research-acceptance/v1'
ACCEPTANCE_EXECUTION_FILES = (
    'scripts/research_experiment_contract.py',
    'scripts/research_consistency.py',
    'scripts/stock_price_map.py',
    'scripts/research_acceptance.py',
    '.agents/skills/stock-research/references/acceptance-gates.md',
)
ACCEPTANCE_SOURCE_FILES = (
    'research_harness_benchmark.py','research_harness_trial.py',
    'research_experiment_proxy.py','research_experiment_contract.py',
    'research_consistency.py','stock_price_map.py','research_acceptance.py',
)
INITIAL_DELIVERY_ADDENDUM = '''# 隔离交付与共享验收
研究方法、适用性、处置和数值仍按本次冻结 canonical。请先读 acceptance-gates.md，再读 research_experiment_contract.py 中 validate_review 的字段约束。
保留完整九节报告和中性 result.json。额外结构块不增加正式产物身份，也不改变报价。报告同时包含 research-audit、可见计算表、experiment-delivery 和 research-acceptance 及其可见表。
experiment-delivery 精确含 schema_version=harness-delivery-checks/v1、review、price_map、research_controls、monitoring；后三项与 result.json 相同。
review 精确包含 precheck{state,d_base_upper_required,reason}、r14{applicability,stress_test,constraint_ids,reason}、d5{applicability,original_rebuild_independent,r21_exit_is_full_clearance,reason}、r9{applicability,benchmark_status,benchmark_currency,constraint_ids,reason}、holding{review_status,constraint_ids,reason}。依据研究填写，不复制示例状态；R14 与共享验收声明一致。
可将 review 和 acceptance JSON 暂存在 outputs，再执行 python3 execution-tools/research_experiment_contract.py render --result outputs/result.json --review outputs/review.json --acceptance outputs/acceptance.json --root . 生成结构块并插入报告；不得用生成块替代研究正文。最后按提示的 check --require-acceptance --root . 回读自检。检查器只验证声明、证据绑定和明确反例，原文与经济语义仍须研究者复核。
'''


def requires_acceptance(manifest):
    """Select the frozen contract explicitly; never upgrade a historical run."""
    if 'acceptance_contract' not in manifest:
        return False
    if manifest['acceptance_contract'] != ACCEPTANCE_CONTRACT:
        raise ValueError('unknown frozen acceptance contract')
    return True

COMMON_RULES = '''# 隔离实验约束（优先于所读技能的默认发布、身份和输出路径）
这是已授权的 DSH/Claude Code harness 对照实验，绝非正式研究发布。全部读写限于当前工作目录。只读取当前目录中的冻结 inputs、framework、.agents；不查找任何原工作区/其它 arm/历史研报/账户，不运行 scheduler/runner/seal/latest/Coze/交易或发消息。不要读取环境变量或凭据。不要填 generator=codex/claude 冒充身份，实际宿主由外层记录。只写 outputs/ 下实验产物，永远不创建正式 stock-research/v4 或 result/v1/seal。没有用户问答环节；缺证明确 unknown 与其影响，不编造。
主研究与子代理请求相同 DeepSeek Flash/high，最多两个本地子代理、深度一层；子代理任务自足，只用本目录原文和输出目录。不用外部 CLI 子代理、MCP、Jev、交易或后台定时器。调用框架/skill按文件读取，不假设专用API。工具失败如实记录，能在本目录范围恢复则恢复，不能完成的项目不得声称已验证。
'''

RESEARCH_PROMPT = COMMON_RULES + '''
研究对象：宁德时代 A 股 300750.SZ；估值截止 2026-10-21（Asia/Shanghai）。research_mode=full，无历史分析基线。这是“固定证据质量任务”：禁止联网和 web_search/web_fetch/curl 等外部取证，OS 仅允许模型连接。现有材料不足的行业、宏观、板块、持仓字段必须披露缺口，不能用记忆补事实。
输入：inputs/data-pack.md 为同一真实公开包；inputs/sources/ 为公开原始 PDF、带页界文本、公告目录及下载来源记录；inputs/source-index.json 是文件/来源列表。framework 下 canonical/compact 为原始冻结方法；.agents/skills/stock-research 和 deep-research-auto 的研究/估值/控制方法仍适用，只有上述隔离交付要求覆盖正式发布规则。
先读 compact、stock-research 和适用 reference；读 canonical 解决具体歧义。建立事实/期间/单位/披露日期/原页表并回财报校验包中缺口与修订冲突。PDF文本部分可能乱码，不能当无内容；用可用 pdftotext/pdfinfo/渲染图片或本地Python查看原PDF，关键财表不只依摘要。不能把期末现金再加当期OCF，不把累计/单季、认缴/实缴、人民币元/亿元、A股/H股/总股本混用。全部重要数字引来源文件+PDF页码；解释没有外部资料可验证的部分。
按本仓框架完成 0–8 九节完整报告，保留适用经营/财务/行业竞争/治理/估值/Terminal/风险/控制/监控/反证。可用两个子任务独立核财务及风险，再由主代理回原文复核关键数字。收入、利润率、PE或更适用模型给low/base/high、理由和算术；五折扣明确范围/归属/敏感性，避免同一风险重复计价。按实际证据独立判断可估性与买入资格，缺证不是强行估值或默认为通过，也不是见缺项便跳过仍可完成的分析。能计算的观察P1/T1须清楚论证，不因冻结而机械清空。完整条件表区分entry/add/holding及persistent/runtime/observation，不把价格或研究完成当执行许可。
只交付以下两个文件，不需要额外正式交付回执：
1. outputs/report.md：中文完整九节（标题“## 0.”到“## 8.”）、完整来源/缺口/最终P1/T1及计算表；研究不是提纲或计划。
2. outputs/result.json：严格JSON，顶层仅 schema_version/code/valuation_date/currency/price_map/research_controls/monitoring/audit。schema_version固定harness-research-experiment/v1，code=300750.SZ，valuation_date=2026-10-21，currency=CNY；price_map/research_controls/monitoring的经济语义按v4但不带meta/generator。audit沿本仓audit-v2的估值链、折扣、风险独占归属、作用范围与合取解除，identity仅code/valuation_date/currency，不填generator，baseline=null（共同无历史输入）。实验JSON不运行正式writer/build，不改全局schema；可自己用Python验算和严格JSON解析。报告与JSON报价/状态必须一致，P1是报告最终明确报价而不是导出重算。最后自行回读两文件，检查有限数、单位、全部算式、关键引用和未知控制一致性。完成后最终回复仅简要列两个路径及仍有的实质缺口。
'''

PROBE_PROMPT = COMMON_RULES + '''
这是综合工具探针，不是正式公司研究。六项都实际尝试，允许诚实报告失败，不能只写将要做：
A. 用文件搜索/读取定位 inputs/probe/metrics.csv；这是明确标记的合成测试数据，非上市公司财务。用shell/Python按元计算收入总和与利润总和，再算整体利润率，不对平均利润率求平均；缺失debt=null不能补0。
B. 委派一个独立本地子代理复核A的算术及null语义；记录其返回结论与是否完成，不能虚构子代理。
C. 实际执行 python3 inputs/probe/flaky.py outputs/flaky-state，首次会可预期exit42（合成故障），读取错误后再次执行一次恢复；记录两次exit_code。不修改fixture脚本来消除错误。
D. 使用原生web search搜索“宁德时代 2026年三季度报告 2026-10-21 巨潮”，尽量找到官方披露；记录实际URL、结果标题与日期，搜索摘要不代表原文已读。
E. 使用原生web fetch打开 https://static.cninfo.com.cn/finalpage/2026-10-21/1225613175.PDF 。不支持PDF或抓取失败要保留真实错误，可用当前目录内的公开下载+pdftotext做一次合理替代；记录实际成功读取内容与文件SHA256，不能把只有摘要当PDF已验证。不调用gemini或付费第三方检索。
F. 写 outputs/probe-result.json：顶层schema_version=harness-tool-probe/v1；arithmetic{revenue,profit,margin,debt}，independent_check{attempted,completed,conclusion}，recovery{first_exit,second_exit,ok}，web{queries,search_succeeded,source_url,fetch_succeeded,fallback_used,pdf_sha256,document_title,published_date,error}，limitations数组。全部依据真实工具结果，未测用null/说明。
两端使用相同提示词和文件；不要读完整研究报告或运行完整估值。本次截止2026-10-21，未来披露不作当时证据。完成前回读JSON，最终回复只给路径和未完成项。
'''

SMOKE_PROMPT = COMMON_RULES + '\n仅做连接和文件写入smoke：用本地文件工具在 outputs/smoke.json 写入 {"ok":true,"value":42}，回读确认后最终答 SMOKE_OK。不联网检索，不开子代理，不读其它文件。\n'


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()


def read_regular(path,limit=16*1024*1024):
    path = Path(path)
    if path.is_symlink():
        raise ValueError('experiment artifacts must not be symlinks')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        info=os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size>limit:
            raise ValueError('experiment artifact must be a bounded regular file')
        with os.fdopen(fd,'rb',closefd=False) as stream:return stream.read(limit+1)
    finally:os.close(fd)


def digest(path):
    return hashlib.sha256(read_regular(path)).hexdigest()


def inventory(root):
    return {p.relative_to(root).as_posix(): digest(p) for p in sorted(Path(root).rglob('*')) if p.is_file()}


def safe_experiment(path):
    path = Path(path).resolve()
    if not any(path.is_relative_to(base.resolve()) and path != base.resolve()
               for base in (EXPERIMENTS,FOLLOWUP_EXPERIMENTS)):
        raise ValueError('experiment must have its own directory under the isolated experiment root')
    return path


def acceptance_execution_files(execution_files):
    """Validate the complete standalone gate before creating any output."""
    names=list(dict.fromkeys([*execution_files,*ACCEPTANCE_EXECUTION_FILES]))
    for name in names:
        relative=Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('execution file must be repository relative')
        read_regular(ROOT/relative)
    if len({Path(name).name for name in names})!=len(names):
        raise ValueError('execution files must have unique basenames')
    return names


def freeze_acceptance_execution(path, execution_files, addendum):
    execution=path/'execution-tools';execution.mkdir()
    for name in execution_files:
        (execution/Path(name).name).write_bytes(read_regular(ROOT/name))
    (execution/'delivery-addendum.md').write_text(addendum)
    return inventory(execution)


def acceptance_research_prompt(research):
    research+='\n\n本轮共同执行与交付补充（覆盖旧提示中只读取目录及无需回执的限制；不改变 canonical 投研方法）：\n'
    research+='允许读取 execution-tools/ 下冻结的交付说明和纯离线检查器。先读 execution-tools/delivery-addendum.md，按其完成报告与结果自检。检查失败要回原文解决；不可删规则、改检查器或伪造通过。无法解决的实质缺口仍照实交付，不以外层停止代替完成。\n'
    research+='本轮强制 stock-research-acceptance/v1：必读 execution-tools/acceptance-gates.md，在报告加入 research-acceptance JSON 块及对应可见验收表。R14 必要证据缺失或仅凭任意假设不能判 passed；缺证保留自身 persistent add 约束。各范围全部有效独立约束解除后才能恢复，保留单条规则内部合法替代路径。证据路径以当前工作区为 root。自检命令：python3 execution-tools/research_experiment_contract.py check --report outputs/report.md --result outputs/result.json --require-acceptance --root .。旧 experiment-delivery 块仍需保留并与新块的 R14 状态一致。\n'
    research+='主代理及最多两个深度一层子代理均使用同一 DeepSeek Flash/high，输出上限32768。给子任务明确范围和自足原文路径；子代理在输出目录持续保存关键证据与中间结果，交接须给结论、原文定位及未决事项。主代理检查真实完成状态；settled 或 max-tokens 不代表 completed。若子代理因长度或可恢复工具故障未正常完成，主代理可用本 harness 原生消息/续做机制至多续做两次，先让其保存简洁交接；全部尝试保留。不能虚构子代理成功，也不要求为形式凑满子代理。主代理最终回读两文件，核验共享交付契约并正常结束；不得只写计划或依赖外层修复。\n'
    return research


def prepare_from_frozen(path, source, *, execution_files, addendum):
    """Copy an immutable original corpus; repairs are separate execution inputs."""
    path=safe_experiment(path);source=safe_experiment(source)
    if path.exists():raise ValueError('existing experiment is immutable; choose a new directory')
    manifest=verify_experiment(source)
    if path.is_relative_to(source) or source.is_relative_to(path):
        raise ValueError('source and new experiment must be disjoint')
    # Keep the original corpus byte-identical. New checker code and its gate
    # reference are independently frozen, including all standalone imports.
    execution_files=acceptance_execution_files(execution_files)
    if not isinstance(addendum,str) or not addendum.strip():raise ValueError('shared addendum required')
    path.mkdir(parents=True,mode=0o700)
    shutil.copytree(source/'frozen',path/'frozen')
    execution=freeze_acceptance_execution(path,execution_files,addendum)
    prompts=path/'prompts';shutil.copytree(source/'prompts',prompts)
    research=acceptance_research_prompt((prompts/'research.txt').read_text())
    (prompts/'research.txt').write_text(research)
    new=dict(manifest)
    new.update(created_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
        source_experiment=str(source),source_manifest_sha256=digest(source/'manifest.json'),
        original_frozen_sha256=manifest['frozen'],frozen=inventory(path/'frozen'),
        execution_tools=execution,prompts=inventory(prompts),
        execution_source_sha256={name:digest(ROOT/'scripts'/name) for name in ACCEPTANCE_SOURCE_FILES},
        delivery_contract='harness-delivery-checks/v1',
        acceptance_contract=ACCEPTANCE_CONTRACT,
        planned=dict(research_per_arm=2,research_timeout_seconds=2400,max_output_tokens=32768,
                     stream_idle_timeout_seconds=180,max_native_child_recoveries=2),
        repair_scope='Execution isolation, independent failure gates, delivery representation only; original methods and source bytes unchanged.')
    if new['frozen']!=manifest['frozen']:raise ValueError('original frozen input changed while copying')
    (path/'manifest.json').write_bytes(encode(new))
    return path


def prepare_experiment(path):
    path = safe_experiment(path)
    if path.exists():
        raise ValueError('existing experiment is immutable; choose a new directory')
    execution_files=acceptance_execution_files([])
    frozen = path / 'frozen'
    frozen.mkdir(parents=True)
    path.chmod(0o700)
    inputs = frozen / 'inputs'
    sources = inputs / 'sources'
    sources.mkdir(parents=True)
    shutil.copyfile(SOURCE_RUN / 'packs/SZ-300750.md', inputs / 'data-pack.md')
    # Full original disclosures, not previous analysts' notes or conclusions.
    selected = sorted({p for pattern in ('finance-*.pdf', 'finance-*.txt', 'main-monthshare.*',
                                       'controls-*.pdf', 'controls-*.txt', 'controls-*.html',
                                       'finance-announcement-source-ledger.json', 'finance-cninfo-directory-p1.json',
                                       'controls-download-log.json') for p in MATERIALS.glob(pattern)
                       if p.suffix in {'.pdf','.txt','.html','.json'}})
    selected = [p for p in selected if p.name not in {'finance-cninfo-entity-get.txt'}]
    for source in selected:
        shutil.copyfile(source, sources / source.name)
    ledger = json.loads((MATERIALS / 'finance-announcement-source-ledger.json').read_text())
    origin = {Path(v['pdf']).name: {k:v.get(k) for k in ('id','title','url','date','pages','sha256')} for v in ledger}
    origin['finance-2026h1.pdf'] = dict(url='https://static.cninfo.com.cn/finalpage/2026-07-24/1225442062.PDF',date='2026-07-24',title='2026年半年度报告')
    origin['main-monthshare.pdf'] = dict(url='https://static.cninfo.com.cn/finalpage/2026-10-08/1225595385.PDF',date='2026-10-08',title='月报表')
    index = [dict(file='inputs/sources/'+p.name, sha256=digest(p), bytes=p.stat().st_size,
                  source=origin.get(p.name, {'lookup':'finance-announcement-source-ledger.json or controls-download-log.json; text inherits corresponding PDF'})) for p in sorted(sources.iterdir())]
    (inputs / 'source-index.json').write_bytes(encode(index))
    (frozen / 'framework').mkdir()
    for name in ('investment_framework.md','investment_framework_compact.md'):
        shutil.copyfile(SOURCE_RUN / 'framework-snapshot' / name, frozen / 'framework' / name)
    for skill in ('stock-research','deep-research-auto'):
        shutil.copytree(ROOT / '.agents/skills' / skill, frozen / '.agents/skills' / skill)
    (frozen / 'AGENTS.md').write_text(COMMON_RULES)
    # Also explicitly read by CC; equivalent bytes, DSH de-duplicates them.
    (frozen / 'CLAUDE.md').write_text(COMMON_RULES)
    (inputs / 'probe').mkdir()
    (inputs / 'probe/metrics.csv').write_text('label,revenue,profit,debt\nsynthetic_A,100000000,10000000,\nsynthetic_B,200000000,50000000,\n')
    (inputs / 'probe/flaky.py').write_text("import pathlib,sys,json\np=pathlib.Path(sys.argv[1])\nif not p.exists():\n p.parent.mkdir(parents=True,exist_ok=True);p.write_text('attempted');print('EXPECTED_TRANSIENT_FIXTURE_ERROR',file=sys.stderr);sys.exit(42)\nprint(json.dumps({'ok':True,'value':42}))\n")
    prompts = path / 'prompts'; prompts.mkdir()
    for task, value in (('smoke',SMOKE_PROMPT),('probe',PROBE_PROMPT),('research',acceptance_research_prompt(RESEARCH_PROMPT))):
        (prompts / (task+'.txt')).write_text(value)
    execution=freeze_acceptance_execution(path,execution_files,INITIAL_DELIVERY_ADDENDUM)
    manifest = dict(schema_version=SCHEMA,created_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
                    policy=dict(production=False,consensus=False,latest=False,seal=False,switch=False),
                    company='300750.SZ',valuation_date='2026-10-21',
                    model='deepseek-flash',effort='high',subagent_model='deepseek-flash',
                    dsh_composition='headless/base, not GUI Standard',
                    source_run=str(SOURCE_RUN.relative_to(ROOT)),
                    frozen=inventory(frozen),prompts=inventory(prompts),execution_tools=execution,
                    execution_source_sha256={name:digest(ROOT/'scripts'/name) for name in ACCEPTANCE_SOURCE_FILES},
                    delivery_contract='harness-delivery-checks/v1',acceptance_contract=ACCEPTANCE_CONTRACT,
                    planned=dict(smoke_per_arm=1,probe_per_arm=3,research_per_arm=1,
                                 probe_timeout_seconds=600,research_timeout_seconds=2400,
                                 max_output_tokens=32768,stream_idle_timeout_seconds=180,max_native_child_recoveries=2),
                    rubric=dict(facts=30,coverage=20,valuation=25,controls=15,delivery=10),
                    limits='Small sample. Full research uses fixed corpus; online capability only screened in probes. Token estimates are not billed invoice.')
    (path / 'manifest.json').write_bytes(encode(manifest))
    return path


def verify_experiment(path):
    path = safe_experiment(path)
    manifest = json.loads((path / 'manifest.json').read_text())
    require_acceptance=requires_acceptance(manifest)
    if require_acceptance:
        required_tools={Path(name).name for name in ACCEPTANCE_EXECUTION_FILES}|{'delivery-addendum.md'}
        if (manifest.get('delivery_contract')!='harness-delivery-checks/v1'
                or not isinstance(manifest.get('execution_tools'),dict)
                or not required_tools.issubset(manifest['execution_tools'])
                or not isinstance(manifest.get('execution_source_sha256'),dict)
                or not set(ACCEPTANCE_SOURCE_FILES).issubset(manifest['execution_source_sha256'])):
            raise ValueError('acceptance manifest requires complete frozen gate dependencies and source hashes')
    if manifest['schema_version'] != SCHEMA or manifest['frozen'] != inventory(path/'frozen') or manifest['prompts'] != inventory(path/'prompts'):
        raise ValueError('frozen experiment input changed')
    if 'execution_tools' in manifest and manifest['execution_tools']!=inventory(path/'execution-tools'):
        raise ValueError('frozen experiment execution tools changed')
    if any(digest(ROOT/'scripts'/name)!=value for name,value in manifest.get('execution_source_sha256',{}).items()):
        raise ValueError('frozen experiment implementation changed')
    return manifest


def validate_artifacts(run_dir, task, *, delivery_contract=False, require_acceptance=False):
    workspace = Path(run_dir) / 'workspace'
    target = workspace / 'outputs' / {'smoke':'smoke.json','probe':'probe-result.json','research':'result.json'}[task]
    result = dict(file_exists=target.is_file(),strict_json=False,errors=[])
    if workspace.is_symlink():
        result['errors'].append('workspace is a symlink');return result
    if not target.is_file():
        result['errors'].append('missing expected file');return result
    def pairs(values):
        obj={}
        for key,value in values:
            if key in obj: raise ValueError('duplicate key')
            obj[key]=value
        return obj
    try:
        if not target.resolve().is_relative_to(workspace.resolve()):raise ValueError('artifact escaped workspace')
        doc=json.loads(read_regular(target,1024*1024),object_pairs_hook=pairs,
                       parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite')))
        def finite(value):
            if isinstance(value,float) and not math.isfinite(value):raise ValueError('nonfinite')
            if isinstance(value,dict):
                for item in value.values():finite(item)
            if isinstance(value,list):
                for item in value:finite(item)
        finite(doc)
        if not isinstance(doc,dict): raise ValueError('expected object')
        result['strict_json']=True
        if task=='smoke':
            if doc != {'ok':True,'value':42}: result['errors'].append('smoke content mismatch')
        elif task=='probe':
            if doc.get('schema_version')!='harness-tool-probe/v1': result['errors'].append('probe schema')
            for name in ('arithmetic','independent_check','recovery','web'):
                if not isinstance(doc.get(name),dict):raise ValueError('probe '+name+' must be an object')
            a=doc.get('arithmetic',{})
            result['arithmetic_correct']=(a.get('revenue')==300000000 and a.get('profit')==60000000 and a.get('margin')==0.2 and a.get('debt') is None)
            result['delegation_reported']=doc.get('independent_check',{}).get('completed') is True
            r=doc.get('recovery',{})
            result['recovery_correct']=r.get('first_exit')==42 and r.get('second_exit')==0 and r.get('ok') is True
            result['search_reported']=doc.get('web',{}).get('search_succeeded') is True
            result['fetch_reported']=doc.get('web',{}).get('fetch_succeeded') is True
            result['reported_fields_require_log_verification']=True
        else:
            required={'schema_version','code','valuation_date','currency','price_map','research_controls','monitoring','audit'}
            if set(doc)!=required:result['errors'].append('research exact fields')
            if doc.get('schema_version')!='harness-research-experiment/v1' or doc.get('code')!='300750.SZ' or doc.get('valuation_date')!='2026-10-21':result['errors'].append('research identity')
            if doc.get('currency')!='CNY':result['errors'].append('research currency')
            for name in ('price_map','research_controls','audit'):
                if not isinstance(doc.get(name),dict):raise ValueError('research '+name+' must be an object')
            if not isinstance(doc.get('monitoring'),list):raise ValueError('research monitoring must be an array')
            report=workspace/'outputs/report.md'
            result['report_exists']=report.is_file()
            if report.exists():
                import re
                if not report.resolve().is_relative_to(workspace.resolve()):raise ValueError('report escaped workspace')
                text=read_regular(report,4*1024*1024).decode('utf-8')
                result['nine_sections']=all(re.search(r'^##\s+'+str(n)+r'\.',text,re.M) for n in range(9))
                if delivery_contract or require_acceptance:
                    from scripts.research_experiment_contract import validate_experiment
                    try:
                        result['delivery_contract']=validate_experiment(text,doc,
                            require_acceptance=require_acceptance,root=workspace)
                    except (ValueError,TypeError,KeyError,RecursionError) as exc:
                        result['delivery_contract']=dict(status='failed',errors=[type(exc).__name__+': '+str(exc)],
                            semantic_source_review_required=True,experiment_only=True,production=False,consensus_eligible=False)
            result['production_acceptance']=False
    except (ValueError,UnicodeError,TypeError,OSError,RuntimeError) as exc:
        result['errors'].append(type(exc).__name__+': '+str(exc))
    return result


def arm_input_status(workspace,expected):
    workspace=Path(workspace).absolute()
    status={}
    for name,value in expected.items():
        path=workspace/name
        try:
            status[name]=(not workspace.is_symlink() and path.resolve(strict=True).is_relative_to(workspace)
                          and digest(path)==value)
        except (OSError,ValueError,RuntimeError):status[name]=False
    return status


def cli_identity():
    identities={}
    for arm,name in (('cc','claude'),('dsh','dsh')):
        path=shutil.which(name)
        if not path:raise ValueError('required experimental CLI unavailable')
        path=Path(path).resolve()
        hasher=hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda:stream.read(1024*1024),b''):hasher.update(chunk)
        identities[arm]=dict(path=str(path),bytes=path.stat().st_size,sha256=hasher.hexdigest())
    package=Path.home()/'.local/lib/node_modules/@deepseek-ai/dsh/package.json'
    if package.is_file():
        identities['dsh'].update(package_version=json.loads(read_regular(package))['version'],
                                 package_json_sha256=digest(package))
    identities['cc']['version_from_installed_binary_name']=Path(identities['cc']['path']).name
    return identities


@contextmanager
def cancellation_scope():
    cancelled=threading.Event()
    previous={}
    if threading.current_thread() is threading.main_thread():
        for sig in (signal.SIGINT,signal.SIGTERM):
            previous[sig]=signal.signal(sig,lambda *_:cancelled.set())
    try:yield cancelled
    finally:
        for sig,handler in previous.items():signal.signal(sig,handler)


def run_pair(path, task, repeat=1, *, timeout=None, input_tokens_semantics=None,
             max_requests=160, budget_usd=3.0,max_output_tokens=16384,stream_idle_timeout=120):
    from scripts.research_experiment_proxy import ObservingProxy
    from scripts.research_harness_trial import run_trial
    manifest=verify_experiment(path)
    require_acceptance=requires_acceptance(manifest)
    for name,value in (('repeat',repeat),('max_requests',max_requests),('max_output_tokens',max_output_tokens)):
        if isinstance(value,bool) or not isinstance(value,int) or value<=0:raise ValueError(name+' must be a positive integer')
    for name,value in (('budget_usd',budget_usd),('stream_idle_timeout',stream_idle_timeout)):
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<=0:
            raise ValueError(name+' must be finite and positive')
    if timeout is not None and (isinstance(timeout,bool) or not isinstance(timeout,(int,float)) or not math.isfinite(timeout) or timeout<=0):
        raise ValueError('timeout must be finite and positive')
    if manifest.get('delivery_contract') and task=='research':
        planned=manifest['planned']
        if (repeat>planned['research_per_arm'] or max_output_tokens!=planned['max_output_tokens']
                or stream_idle_timeout!=planned['stream_idle_timeout_seconds']
                or timeout!=planned['research_timeout_seconds']):
            raise ValueError('research execution differs from frozen follow-up plan')
    path=Path(path)
    stem=f'{task}-{repeat:02d}'
    pair=path/'runs'/stem
    pair.mkdir(parents=True,exist_ok=False)
    prompt=(path/'prompts'/f'{task}.txt').read_bytes()
    # Read only the existing approved provider credential; never print/copy it.
    settings=json.loads((Path.home()/'.claude/settings.json').read_text())
    env=settings.get('env',{})
    key=env.get('ANTHROPIC_AUTH_TOKEN') or env.get('ANTHROPIC_API_KEY')
    if not isinstance(key,str) or not key.strip():raise ValueError('approved DeepSeek credential unavailable')
    if env.get('ANTHROPIC_BASE_URL','').rstrip('/')!='https://api.deepseek.com/anthropic':raise ValueError('existing CC provider is not the approved DeepSeek endpoint')
    protected=inventory(path/'frozen')
    arms=['cc','dsh'] if repeat%2 else ['dsh','cc']
    implementation={name:digest(ROOT/'scripts'/name) for name in
        ('research_harness_benchmark.py','research_harness_trial.py','research_experiment_proxy.py')}
    if manifest.get('delivery_contract'):
        implementation.update({name:digest(ROOT/'scripts'/name) for name in (
            'research_experiment_contract.py','research_consistency.py','stock_price_map.py')})
    if require_acceptance:
        implementation['research_acceptance.py']=digest(ROOT/'scripts/research_acceptance.py')
    (pair/'configuration.json').write_bytes(encode(dict(
        created_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
        source_sha256=implementation,prompt_sha256=hashlib.sha256(prompt).hexdigest(),
        cli=cli_identity(),
        order=arms,task=task,repeat=repeat,input_tokens_semantics=input_tokens_semantics,
        model='deepseek-flash',effort='high',max_output_tokens=max_output_tokens,
        stream_idle_timeout_seconds=stream_idle_timeout,online=task!='research',
        provider_server_tools_allowed=task!='research',
        max_requests=max_requests,budget_usd=budget_usd,budget_scope='per_arm',
        production=False,consensus=False)))
    with cancellation_scope() as cancelled, ObservingProxy(key,pair/'requests.jsonl',arms,max_requests=max_requests,budget_usd=budget_usd,input_tokens_semantics=input_tokens_semantics,allow_server_tools=task!='research') as proxy:
        jobs={}
        arm_cancelled={arm:threading.Event() for arm in arms}
        cancellation_reasons={}
        finished=set()
        with ThreadPoolExecutor(max_workers=2) as pool:
            for arm in arms:
                run_dir=pair/arm;run_dir.mkdir()
                workspace=run_dir/'workspace';shutil.copytree(path/'frozen',workspace)
                if manifest.get('execution_tools'):
                    shutil.copytree(path/'execution-tools',workspace/'execution-tools')
                (workspace/'outputs').mkdir()
                # A real repository root gives both filesystem skill providers the same root.
                import subprocess
                subprocess.run(['/usr/bin/git','init','-q',str(workspace)],check=True,stdin=subprocess.DEVNULL,capture_output=True)
                jobs[arm]=pool.submit(run_trial,arm,workspace,run_dir,prompt,proxy.url(arm),
                                      timeout=timeout or (1800 if task=='research' else 600),online=task!='research',
                                      cancelled=arm_cancelled[arm],max_output_tokens=max_output_tokens,
                                      stream_idle_timeout=stream_idle_timeout)
                time.sleep(0.2)
            pending=set(jobs.values())
            while pending:
                _,pending=wait(pending,timeout=.25)
                budget=proxy.summary()
                for arm,future in jobs.items():
                    if future.done() and arm not in finished:
                        proxy.stop_arm(arm,'ArmFinished');finished.add(arm)
                    if arm in finished:continue
                    if cancelled.is_set():
                        arm_cancelled[arm].set();cancellation_reasons[arm]='human_cancelled'
                        proxy.stop_arm(arm,'ArmCancelled')
                    elif budget.get('by_arm',{}).get(arm,{}).get('subsequent_requests_blocked'):
                        arm_cancelled[arm].set()
                        cancellation_reasons[arm]=budget['by_arm'][arm].get('block_reason')
            outcomes={}
            for arm,future in jobs.items():
                try:
                    outcomes[arm]=future.result()
                except Exception as exc:
                    outcomes[arm]=dict(status='infrastructure_failed',success=False,
                                       error_type=type(exc).__name__,error=str(exc))
                outcomes[arm]['supervisor_cancellation_reason']=cancellation_reasons.get(arm)
        # __exit__ drains or explicitly records incomplete in-flight requests.
    usage=proxy.summary()
    for arm in arms:
        outcomes[arm]['artifacts']=validate_artifacts(pair/arm,task,
            delivery_contract=bool(manifest.get('delivery_contract')),require_acceptance=require_acceptance)
        artifact=outcomes[arm]['artifacts']
        outcomes[arm]['process_success']=outcomes[arm].get('success',False)
        outcomes[arm]['experimental_envelope_pass']=bool(artifact['strict_json'] and not artifact['errors']
            and (task!='research' or artifact.get('nine_sections')))
        outcomes[arm]['domain_quality_requires_review']=task=='research'
        outcomes[arm]['experimental_delivery_contract_pass']=artifact.get('delivery_contract',{}).get('status')=='passed'
        outcomes[arm]['input_unchanged']=arm_input_status(pair/arm/'workspace',manifest['frozen'])
        outcomes[arm]['execution_tools_unchanged']=arm_input_status(pair/arm/'workspace'/'execution-tools',manifest.get('execution_tools',{}))
    summary=dict(task=task,repeat=repeat,order=arms,prompt_sha256=hashlib.sha256(prompt).hexdigest(),
                 source_sha256=implementation,outcomes=outcomes,proxy=usage,
                 implementation_unchanged=all(digest(ROOT/'scripts'/name)==value for name,value in implementation.items()),
                 frozen_unchanged=protected==inventory(path/'frozen'),
                 runtime_dependencies_equal=bool(all(outcomes[a].get('runtime_dependencies_sha256') for a in arms)
                     and len({outcomes[a].get('runtime_dependencies_sha256') for a in arms})==1))
    (pair/'summary.json').write_bytes(encode(summary))
    print(json.dumps({'pair':str(pair),'task':task,'outcomes':{a:{'status':v.get('status'),'success':v.get('success'),'artifacts':v['artifacts']} for a,v in outcomes.items()},'proxy':usage},ensure_ascii=False),flush=True)
    return summary


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('prepare','smoke','probe','research'))
    parser.add_argument('--directory',required=True,type=Path)
    parser.add_argument('--repeat',type=int,default=1)
    parser.add_argument('--timeout',type=float)
    parser.add_argument('--input-tokens-semantics',choices=('total','uncached'))
    parser.add_argument('--max-requests',type=int,default=160)
    parser.add_argument('--budget-usd',type=float,default=3.0)
    parser.add_argument('--max-output-tokens',type=int,default=16384)
    parser.add_argument('--stream-idle-timeout',type=float,default=120)
    parser.add_argument('--execute',action='store_true',help='Explicitly run paid isolated model trials')
    args=parser.parse_args(argv)
    if args.mode=='prepare':print(prepare_experiment(args.directory));return 0
    if not args.execute:parser.error('model trials require --execute')
    run_pair(args.directory,args.mode,args.repeat,timeout=args.timeout,input_tokens_semantics=args.input_tokens_semantics,
             max_requests=args.max_requests,budget_usd=args.budget_usd,
             max_output_tokens=args.max_output_tokens,stream_idle_timeout=args.stream_idle_timeout)
    return 0


if __name__=='__main__':
    sys.path.insert(0,str(ROOT))
    raise SystemExit(main())
