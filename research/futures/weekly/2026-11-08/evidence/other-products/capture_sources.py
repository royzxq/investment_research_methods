import requests, json, hashlib
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
base=Path(__file__).parent
sources=[
('ma-port','https://nenghua.mysteel.com/a/26110414/7DB614888B0D3ECB.html'),
('ma-nz','https://www.nzfco.com/research/morning/30379'),
('sr-start','https://www.msweet.com.cn/eportal/ui?articleKey=3223237&columnId=1014195&pageId=1014425'),
('sr-clear','https://www.msweet.com.cn/eportal/ui?articleKey=3222944&columnId=1014253&pageId=1014425'),
('sr-spot','https://www.msweet.com.cn/eportal/ui?articleKey=3223266&columnId=1014067&pageId=1014425'),
('sr-estimate','https://www.msweet.com.cn/eportal/ui?articleKey=3222055&columnId=1014243&pageId=1014425'),
('cf-yarn','https://news.10jqka.com.cn/20261106/c681546416.shtml'),
('cf-cnce','https://www.cottonchina.org.cn/cncenew/'),
('ma-rules','https://www.czce.com.cn/cn/uploadfile/2024/02/07/20240207154824122.pdf')]
index=[]
for slug,url in sources:
 rec={'id':slug,'url':url,'captured_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()}
 try:
  r=requests.get(url,timeout=25,headers={'User-Agent':'Mozilla/5.0'})
  ext='.pdf' if 'pdf' in r.headers.get('content-type','') else '.html'
  path=base/(slug+ext)
  path.write_bytes(r.content)
  rec.update(status=r.status_code,path=str(path),sha256=hashlib.sha256(r.content).hexdigest(),content_type=r.headers.get('content-type'))
 except Exception as e:rec['error']=str(e)
 index.append(rec)
(base/'capture-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(index,ensure_ascii=False,indent=2))
