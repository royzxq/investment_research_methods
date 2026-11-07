import requests,json,hashlib
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
base=Path(__file__).parent
sources=[('ma-gl9','https://www.glqh.com/jyts/50836.jhtml'),('ma-gl6','https://www.glqh.com/jyts/50834.jhtml'),('ma-gl9-margin','https://www.glqh.com/u/cms/www/202611/06163628q0sl.pdf'),('ma-hicend-margin','https://m.hicend.com.cn/h5/CommonArticleDetail/16193'),('rb-storage','https://www.shfe.com.cn/products/futures/metal/ferrousandpreciousmetal/rb_f/attach/202206/t20220630_798893.html'),('rb-rules','https://www.shfe.com.cn/regulation/exchangerules/productrules/202512/t20251231_829962.html'),('ma-storage','https://www.czce.com.cn/cn/rootfiles/2022/04/27/1644404734921877-1644404734985457.pdf'),('sr-storage','https://www.hsqh.net/col230/4842'),('cf-yarn-list','https://www.mysteel.com/oilchem/article/k5qez6/'),('czce-holiday-lineage','https://finance.eastmoney.com/a/202512173594248238.html')]
index=[]
for slug,url in sources:
 rec={'id':slug,'url':url,'captured_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()}
 try:
  r=requests.get(url,timeout=25,headers={'User-Agent':'Mozilla/5.0'})
  ext='.pdf' if 'pdf' in r.headers.get('content-type','') else '.html'
  path=base/(slug+ext);path.write_bytes(r.content)
  rec.update(status=r.status_code,path=str(path),sha256=hashlib.sha256(r.content).hexdigest())
  if slug in ['cf-yarn-list','czce-holiday-lineage']:
   s=BeautifulSoup(r.content,'html.parser')
   for a in s.find_all('a',href=True):
    if '20261030-20261105' in a.get_text() or 'czce.com' in a['href']:print(slug,a.get_text(' ',strip=True),a['href'])
 except Exception as e:rec['error']=str(e)
 index.append(rec)
(base/'capture-extra-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(index,ensure_ascii=False,indent=2))
