from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parents[4]
base=Path(__file__).resolve().parent
kind,part=sys.argv[1],int(sys.argv[2])
spec=json.loads((base/(kind+'-corpus.json')).read_text())
for item in spec['parts'][part]:
 p=root/item['path'];raw=p.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=item['sha256']:raise SystemExit('source changed')
 text=raw.decode('utf-8')[item['start']:item['end']]
 if hashlib.sha256(text.encode()).hexdigest()!=item['text_sha256']:raise SystemExit('span changed')
 print(json.dumps({'id':item['id'],'text':text},ensure_ascii=False,separators=(',',':')))
print(json.dumps({'end_of_part':part,'items':len(spec['parts'][part])}))
