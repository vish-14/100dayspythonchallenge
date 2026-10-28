import json,sys
d=sys.argv[1]
t=open(sys.argv[2]).read()
t=t.replace('/*TIMELINE*/',json.dumps(json.load(open('timeline.json')),ensure_ascii=False)).replace('/*MOUTHS*/',open('mouths.json').read())
open(f'{d}/index.html','w').write(t)
