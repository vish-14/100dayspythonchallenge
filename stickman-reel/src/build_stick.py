import json,sys
d=sys.argv[1]
t=open(sys.argv[2]).read()
tl=json.load(open('timeline.json')); vd=json.load(open('voices/voices.json'))
for ln in tl['lines']: ln['dur']=vd[ln['id']]['dur']
t=t.replace('/*TIMELINE*/',json.dumps(tl,ensure_ascii=False)).replace('/*MOUTHS*/',open('mouths.json').read())
open(f'{d}/index.html','w').write(t)
