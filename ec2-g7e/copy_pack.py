#!/usr/bin/env python3
"""Copy the Pennyroyal /workspace tree from a RunPod network volume to S3.

Ranged GET from the RunPod S3 gateway, multipart PUT to our bucket. The RunPod
credential is read from SSM at run time and never touches disk.
"""

import concurrent.futures as cf
import json
import os
import sys
import threading
import time

import boto3
from botocore.config import Config

SRC_BUCKET = "szjxc7ha34"
SRC_ENDPOINT = "https://s3api-us-nc-2.runpod.io"
SRC_REGION = "us-nc-2"
DST_BUCKET = os.environ["DST_BUCKET"]
DST_REGION = os.environ.get("DST_REGION", "us-east-1")
DST_PREFIX = "workspace/"
PREFIXES = ["models/pennyroyal/", "env/"]
PART = 256 << 20
WORKERS = int(os.environ.get("COPY_WORKERS", "16"))

_print_lock = threading.Lock()


def log(*a):
    with _print_lock:
        print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)


def clients():
    ssm = boto3.client("ssm", region_name="us-east-1")
    cred = json.loads(
        ssm.get_parameter(Name="/gamesummoner/runpod/s3", WithDecryption=True)["Parameter"]["Value"]
    )
    cfg = Config(max_pool_connections=WORKERS * 2, retries={"max_attempts": 10, "mode": "standard"})
    src = boto3.client(
        "s3",
        endpoint_url=SRC_ENDPOINT,
        region_name=SRC_REGION,
        aws_access_key_id=cred["k"],
        aws_secret_access_key=cred["s"],
        config=cfg,
    )
    dst = boto3.client("s3", region_name=DST_REGION, config=cfg)
    return src, dst


def listing(src):
    out = []
    for p in PREFIXES:
        tok = None
        while True:
            kw = {"Bucket": SRC_BUCKET, "Prefix": p, "MaxKeys": 1000}
            if tok:
                kw["ContinuationToken"] = tok
            r = src.list_objects_v2(**kw)
            for o in r.get("Contents", []):
                if not o["Key"].endswith("/"):
                    out.append((o["Key"], o["Size"]))
            tok = r.get("NextContinuationToken")
            if not tok:
                break
    return out


def already_there(dst, key, size):
    try:
        h = dst.head_object(Bucket=DST_BUCKET, Key=DST_PREFIX + key)
        return h["ContentLength"] == size
    except Exception:
        return False


def copy_small(src, dst, key, size):
    body = src.get_object(Bucket=SRC_BUCKET, Key=key)["Body"].read()
    if len(body) != size:
        raise IOError(f"short read {key}: {len(body)} != {size}")
    dst.put_object(Bucket=DST_BUCKET, Key=DST_PREFIX + key, Body=body)


def copy_big(src, dst, key, size):
    up = dst.create_multipart_upload(Bucket=DST_BUCKET, Key=DST_PREFIX + key)["UploadId"]
    ranges = [(i, o, min(PART, size - o)) for i, o in enumerate(range(0, size, PART))]
    done = {}
    t0 = time.time()
    counter = [0]

    def one(job):
        i, off, length = job
        b = src.get_object(
            Bucket=SRC_BUCKET, Key=key, Range=f"bytes={off}-{off + length - 1}"
        )["Body"].read()
        if len(b) != length:
            raise IOError(f"short part {i} of {key}: {len(b)} != {length}")
        e = dst.upload_part(
            Bucket=DST_BUCKET, Key=DST_PREFIX + key, UploadId=up, PartNumber=i + 1, Body=b
        )["ETag"]
        with _print_lock:
            counter[0] += 1
            n = counter[0]
        if n % 20 == 0:
            gb = n * PART / 1e9
            log(f"  {key}: {n}/{len(ranges)} parts, {gb:.1f} GB, {gb / (time.time() - t0):.0f} MB/s")
        return i, e

    try:
        with cf.ThreadPoolExecutor(WORKERS) as pool:
            for i, e in pool.map(one, ranges):
                done[i] = e
        dst.complete_multipart_upload(
            Bucket=DST_BUCKET,
            Key=DST_PREFIX + key,
            UploadId=up,
            MultipartUpload={
                "Parts": [{"PartNumber": i + 1, "ETag": done[i]} for i in sorted(done)]
            },
        )
    except Exception:
        dst.abort_multipart_upload(Bucket=DST_BUCKET, Key=DST_PREFIX + key, UploadId=up)
        raise


def main():
    src, dst = clients()
    objs = listing(src)
    total = sum(s for _, s in objs)
    log(f"{len(objs)} objects, {total / 1e9:.2f} GB -> s3://{DST_BUCKET}/{DST_PREFIX}")

    todo = [(k, s) for k, s in objs if not already_there(dst, k, s)]
    log(f"{len(objs) - len(todo)} already present, {len(todo)} to copy")

    small = [(k, s) for k, s in todo if s <= PART]
    big = sorted([(k, s) for k, s in todo if s > PART], key=lambda x: -x[1])

    log(f"small: {len(small)} objects")
    with cf.ThreadPoolExecutor(WORKERS) as pool:
        list(pool.map(lambda ks: copy_small(src, dst, *ks), small))
    log("small done")

    for k, s in big:
        log(f"big: {k} ({s / 1e9:.2f} GB)")
        t = time.time()
        copy_big(src, dst, k, s)
        log(f"big done: {k} in {time.time() - t:.0f}s ({s / 1e6 / (time.time() - t):.0f} MB/s)")

    log("verifying")
    bad = [(k, s) for k, s in objs if not already_there(dst, k, s)]
    if bad:
        log(f"MISMATCH on {len(bad)}: {bad[:5]}")
        sys.exit(1)
    log(f"VERIFIED {len(objs)} objects, {total / 1e9:.2f} GB")


if __name__ == "__main__":
    main()
