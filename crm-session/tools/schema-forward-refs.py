import re,sys
s=open(sys.argv[1]).read().split('\n')
created={}
for i,l in enumerate(s):
    m=re.match(r'CREATE TABLE (?:public\.)?(\w+)',l)
    if m: created.setdefault(m.group(1),i)
cur=None
for i,l in enumerate(s):
    m=re.match(r'CREATE TABLE (?:public\.)?(\w+)',l)
    if m: cur=m.group(1)
    if l.startswith(');'): cur=None
    if cur:
        for r in re.findall(r'REFERENCES\s+(?:public\.)?(\w+)',l):
            if r in created and created[r]>i and r!=cur: print(f"{i+1}: {cur} -> {r} (created at {created[r]+1})")
