# Local TRELLIS launch (this box)

Source: `docs/local_dev.md` L106-129, `src/tools/trellis_server.py` L1-20, `scripts/local_gpu.py` L117-119.

## Launch (from the TRELLIS venv, NOT maestro's venv)

```
<trellis_python> src/tools/trellis_server.py \
  --repo <trellis2 repo> --weights <trellis weights> \
  --host 127.0.0.1 --port 8189 \
  --stage-dir "" --ptype 512
```

Mandatory on this box:
- `--stage-dir ""` — default copies weights into `/dev/shm` (14 GB tmpfs, stays resident). Empty
  string loads straight from `--weights` instead.
- `--ptype 512` (the default) — server always warms `{ptype, "512"}`, so requesting `1024_cascade`
  loads TWO pipelines and peaks ~36 GB host RAM → OOM killer took down the whole desktop session
  twice on 2026-08-21.

`scripts/local_gpu.py` already launches with both flags correct — prefer reusing that over a raw
invocation.

## Health check

```
curl http://127.0.0.1:8189/health
# {"status": "ok", "loaded": <bool>, "warm": <bool>, ...boot timing...}
```

Wait for `"warm": true` before sending a generate request (prod's worker entrypoint gates
registration on this).

## Image -> GLB request

```
curl -X POST "http://127.0.0.1:8189/generate?ptype=512&texture=2048" \
  --data-binary @inputs/enemy-knight.png \
  -H "Content-Type: image/png" \
  -o out/enemy-knight.glb
```

Python equivalent:

```python
import requests
png = open("inputs/enemy-knight.png", "rb").read()
r = requests.post(
    "http://127.0.0.1:8189/generate",
    params={"ptype": "512", "texture": 2048},
    data=png,
    headers={"Content-Type": "image/png"},
)
r.raise_for_status()
open("out/enemy-knight.glb", "wb").write(r.content)
```

Returns `200` with `model/gltf-binary` bytes, or `500` on failure.

## No-queue CLI path

No standalone CLI script found for PNG->GLB outside the queue/worker path
(`scripts/worker-mesh-entrypoint.sh` calls `trellis_server.py` directly; the actual
enqueue/dispatch is in the maestro asset chain, not a bare CLI). The `/generate` HTTP endpoint
above IS the no-queue path — hit it directly with curl/requests against a running
`trellis_server.py` process, bypassing maestro's job queue entirely.
