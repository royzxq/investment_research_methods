import requests,json,hashlib
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
base=Path(__file__).parent
url='https://www.mysteel.com/oilchem/a/26110518/9457984B9DAD0CAD.html'
r=requests.get(url,timeout=25,headers={'User-Agent':'Mozilla/5.0'})
p=base/'cf-weekly.html';p.write_bytes(r.content)
rec={'id':'cf-weekly','url':url,'captured_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'status':r.status_code,'path':str(p),'sha256':hashlib.sha256(r.content).hexdigest()}
(base/'capture-cf-index.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
s=BeautifulSoup(r.content,'html.parser')
for t in s(['script','style']):t.decompose()
t=s.get_text(' ',strip=True);i=t.find('[纯棉纱周评]')
print(rec)
print(t[max(0,i):i+2100])
