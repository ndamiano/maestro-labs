import re,sys
OPEN={"straight":["NS","EW","NS","EW"],"corner":["NE","ES","SW","WN"],"tee":["NES","ESW","NSW","NWE"]}
D={"N":(0,-1),"E":(1,0),"S":(0,1),"W":(-1,0)}; OPP={"N":"S","S":"N","E":"W","W":"E"}
txt=open(sys.argv[1]).read(); blocks=re.split(r"\n(?=LEVEL )",txt[txt.index("LEVEL 1 "):])
seen={}
for b in blocks:
    lines=[l.split() for l in b.strip().splitlines() if l.strip() and not l.startswith("```")]
    head=lines[0]; num=head[1]; issues=[]
    if not any(l[0]=="MIN" for l in lines): print(f"L{num}: TRUNCATED"); continue
    cells={}; src=0; dem=0; mn=None; W=H=0; rot=0
    for l in lines[1:]:
        k=l[0]
        if k=="BOARD": W,H=int(l[1]),int(l[2])
        elif k=="MIN": mn=int(l[1])
        else:
            x,y=int(l[1]),int(l[2])
            if (x,y) in cells: issues.append(f"cell collision at {x},{y}")
            if not(0<=x<W and 0<=y<H): issues.append(f"off board {x},{y}")
            if k=="source": cells[(x,y)]=set(l[4:]); src+=int(l[3])
            elif k=="plant": cells[(x,y)]={l[4]}; dem+=int(l[3])
            else:
                shape,cap,i,t,lk=l[3],int(l[4]),int(l[5]),int(l[6]),int(l[7])
                cells[(x,y)]=set(OPEN[shape][t])
                if lk and i!=t: issues.append(f"locked pipe {x},{y} init!=target")
                if not lk: rot+=(t-i)%4 if shape!="straight" else (t-i)%2
    if src<dem: issues.append(f"source {src} < demand {dem}")
    for (x,y),o in cells.items():
        for d in o:
            nx,ny=x+D[d][0],y+D[d][1]
            if OPP[d] not in cells.get((nx,ny),set()): issues.append(f"open end {x},{y}->{d}")
    if mn is not None and mn!=rot: issues.append(f"MIN {mn} but rotations {rot}")
    key=tuple(sorted((k,tuple(sorted(v))) for k,v in cells.items()))
    if key in seen: issues.append(f"same layout as L{seen[key]}")
    seen.setdefault(key,num)
    print(f"L{num}: {'ok' if not issues else '; '.join(dict.fromkeys(issues))}")
