import json, sqlite3, collections, datetime as dt
db = sqlite3.connect('platform-2026-09-06.db'); db.row_factory = sqlite3.Row
bill = collections.defaultdict(lambda: {'amount':0,'ms':0,'gb':0})
for r in json.load(open('billing.json')):
    b = bill[r['podId']]; b['amount'] += r['amount']; b['ms'] += r['timeBilledMs']; b['gb'] = max(b['gb'], r['diskSpaceBilledGB'])
workers = {w['id']: dict(w) for w in db.execute('select * from workers')}
pod_of = {wid: w['pod_id'] for wid, w in workers.items()}
pod_gpu = {w['pod_id']: (w['gpu_type'] or '?').replace('NVIDIA ','') for w in workers.values() if w['pod_id']}
pod_queue = {w['pod_id']: w['queue'] for w in workers.values() if w['pod_id']}
rate = {p: b['amount']/(b['ms']/3.6e6) for p,b in bill.items() if b['ms']}
games = list(db.execute("select * from games where created_at > strftime('%s','2026-09-04') order by created_at"))
# per pod: total exec seconds on it, to allocate pod's full bill by share
pod_exec = collections.defaultdict(float)
for j in db.execute("select worker_id, exec_seconds from jobs where status='done' and exec_seconds is not null"):
    if j['worker_id'] in pod_of: pod_exec[pod_of[j['worker_id']]] += j['exec_seconds']
def fmt(s): return dt.datetime.utcfromtimestamp(s).strftime('%m-%d %H:%M')
grand = collections.Counter()
for g in games:
    print(f"\n=== {g['title'][:60]}  ({g['id']}, {g['status']})")
    for b in db.execute('select * from builds where game_id=? order by queued_at', (g['id'],)):
        jobs = list(db.execute("select * from jobs where build_id=?", (b['id'],)))
        byq = collections.defaultdict(lambda: collections.Counter())
        marg = 0; alloc = 0; missing = set()
        for j in jobs:
            q = byq[j['queue']]; q['n'] += 1
            if j['status'] != 'done': q['fail'] += 1; continue
            es = j['exec_seconds'] or 0; q['exec'] += es
            pod = pod_of.get(j['worker_id'])
            if pod in rate:
                marg += es/3600*rate[pod]
                alloc += bill[pod]['amount'] * (es/pod_exec[pod] if pod_exec[pod] else 0)
            else: missing.add(pod or j['worker_id'])
        wall = (b['finished_at'] or 0) - (b['started_at'] or 0)
        qs = ' '.join(f"{q}:{c['n']}j/{c['exec']:.0f}s" + (f"/{c['fail']}fail" if c['fail'] else '') for q,c in sorted(byq.items()))
        print(f"  {b['kind']:6} {b['status']:9} steps={b['steps']:>3} wall={wall/60:5.1f}m  {qs}")
        print(f"         marginal=${marg:.3f}  allocated=${alloc:.3f}" + (f"  UNPRICED pods: {missing}" if missing else ''))
        grand[(b['kind'], b['status'], 'marg')] += marg; grand[(b['kind'], b['status'], 'alloc')] += alloc; grand[(b['kind'], b['status'], 'n')] += 1
print('\n=== totals by build kind/status'); 
for k in sorted({(a,b) for a,b,_ in grand}):
    print(f"  {k[0]:6} {k[1]:9} n={grand[k+('n',)]}  marginal=${grand[k+('marg',)]:.2f}  allocated=${grand[k+('alloc',)]:.2f}")
print('\n=== pods in window: bill vs worked')
rows=[]
for p,b in bill.items():
    hrs=b['ms']/3.6e6; worked=pod_exec.get(p,0)/3600
    rows.append((pod_queue.get(p,'UNREG'), pod_gpu.get(p,'?')[:28], p, hrs, worked, b['amount'], b['gb'], rate.get(p,0)))
rows.sort()
tot=collections.Counter()
for q,gpu,p,hrs,worked,amt,gb,r in rows:
    print(f"  {q:6} {gpu:28} {p} billed={hrs*60:6.1f}m worked={worked*60:6.1f}m ${amt:.3f} ${r:.2f}/h disk={gb}GB")
    tot[(q,'amt')]+=amt; tot[(q,'billed')]+=hrs; tot[(q,'worked')]+=worked
print()
for q in sorted({k[0] for k in tot}):
    print(f"  {q:6} billed={tot[(q,'billed')]:.2f}h worked={tot[(q,'worked')]:.2f}h util={100*tot[(q,'worked')]/max(tot[(q,'billed')],1e-9):.0f}% ${tot[(q,'amt')]:.2f}")

print('\n=== per game: llm (by build) + art (by game, allocated pod cost)')
def alloc_jobs(rows):
    marg=alloc=exec_=0; n=fail=0
    for j in rows:
        n+=1
        if j['status']!='done': fail+=1; continue
        es=j['exec_seconds'] or 0; exec_+=es; pod=pod_of.get(j['worker_id'])
        if pod in rate: marg+=es/3600*rate[pod]; alloc+=bill[pod]['amount']*(es/pod_exec[pod])
    return n,fail,exec_,marg,alloc
tot=collections.Counter()
for g in games:
    builds=list(db.execute('select * from builds where game_id=? order by queued_at',(g['id'],)))
    first=[b for b in builds if b['kind']=='build']
    llm_first=alloc_jobs(db.execute("select * from jobs where build_id in (%s)"%','.join('?'*len(first)),[b['id'] for b in first]))
    llm_all=alloc_jobs(db.execute("select * from jobs where build_id in (%s)"%','.join('?'*len(builds)),[b['id'] for b in builds]))
    art=alloc_jobs(db.execute("select * from jobs where game_id=? and queue in ('image','video','mesh')",(g['id'],)))
    wall=sum((b['finished_at']-b['started_at']) for b in first)/60
    print(f"{g['title'][:38]:38} builds={len(first)} wall={wall:5.1f}m  llm(one-shot)={llm_first[4]:.2f}  art={art[4]:.2f} ({art[0]}j,{art[1]}fail)  ONE-SHOT=${llm_first[4]+art[4]:.2f}   all-builds llm={llm_all[4]:.2f} total=${llm_all[4]+art[4]:.2f}")
    tot['oneshot']+=llm_first[4]+art[4]; tot['all']+=llm_all[4]+art[4]; tot['art']+=art[4]; tot['n']+=1
print(f"\nmean one-shot ${tot['oneshot']/tot['n']:.2f}/game   mean incl. fix/change ${tot['all']/tot['n']:.2f}/game   art share of one-shot {100*tot['art']/tot['oneshot']:.0f}%")
