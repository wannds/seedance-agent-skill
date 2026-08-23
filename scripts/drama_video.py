#!/usr/bin/env python3
"""Zero-dependency CLI for the drama New API video gateway."""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_env():
    path = os.path.join(SKILL_DIR, ".env")
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def config(args):
    base = (os.environ.get("DRAMA_BASE_URL") or "").rstrip("/")
    if not base:
        raise SystemExit("DRAMA_BASE_URL is missing; set the user's gateway origin in .env or the environment")
    token = os.environ.get("DRAMA_API_KEY")
    if not token:
        raise SystemExit("DRAMA_API_KEY is missing; set it in .env or the environment")
    model = args.model or os.environ.get("DRAMA_MODEL", "seedance-2.0-fast")
    endpoint = args.endpoint or os.environ.get("DRAMA_ENDPOINT", "auto")
    if endpoint == "auto":
        endpoint = "generations" if "0826" in model else "videos"
    if endpoint not in {"videos", "generations"}:
        raise SystemExit("DRAMA_ENDPOINT must be auto, videos, or generations")
    return base, token, model, endpoint


def request_json(method, url, token, payload=None, timeout=60):
    data = json.dumps(payload, ensure_ascii=False).encode() if payload is not None else None
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Authorization", f"Bearer {token}")
    if data is not None:
        request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", "replace")
            return response.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            detail = json.loads(raw)
        except json.JSONDecodeError:
            detail = raw
        return exc.code, detail
    except urllib.error.URLError as exc:
        raise SystemExit(f"network error: {exc}") from exc


def check(status, payload):
    if status >= 400:
        raise SystemExit(f"HTTP {status}: {json.dumps(payload, ensure_ascii=False)}")


def create_payload(args, model, endpoint):
    payload = {
        "model": model,
        "prompt": args.prompt,
        "seconds": args.seconds,
        "resolution": args.resolution,
        "aspect_ratio": args.aspect_ratio,
    }
    if endpoint == "videos":
        payload["duration"] = args.seconds
    if args.generate_audio:
        payload["generate_audio"] = True
    if args.seed is not None:
        payload["seed"] = args.seed
    if args.negative_prompt:
        payload["negative_prompt"] = args.negative_prompt
    if args.references:
        payload["references"] = [parse_reference(value) for value in args.references]
    return payload


def parse_reference(value):
    fields = dict(part.split("=", 1) for part in value.split(" ") if "=" in part)
    for required in ("type", "role", "source"):
        if not fields.get(required):
            raise SystemExit(f"reference needs type= role= source=: {value}")
    return {"type": fields["type"], "role": fields["role"], "source": fields["source"]}


def create(args):
    base, token, model, endpoint = config(args)
    path = "/v1/video/generations" if endpoint == "generations" else "/v1/videos"
    status, payload = request_json("POST", base + path, token, create_payload(args, model, endpoint))
    check(status, payload)
    task_id = payload.get("id") or payload.get("task_id")
    if not task_id:
        raise SystemExit(f"create response has no task id: {payload}")
    print(json.dumps({"task_id": task_id, "model": model, "endpoint": endpoint}, ensure_ascii=False))
    return task_id


def poll(args, task_id=None):
    base, token, model, endpoint = config(args)
    task_id = task_id or args.task_id
    path = f"/v1/video/generations/{urllib.parse.quote(task_id)}" if endpoint == "generations" else f"/v1/videos/{urllib.parse.quote(task_id)}"
    deadline = time.time() + args.timeout
    while time.time() < deadline:
        status, payload = request_json("GET", base + path, token)
        check(status, payload)
        state = payload.get("status")
        print(json.dumps({"task_id": task_id, "status": state, "progress": payload.get("progress")}, ensure_ascii=False), file=sys.stderr)
        if state in {"completed", "failed"}:
            print(json.dumps(payload, ensure_ascii=False))
            if state == "failed":
                raise SystemExit(1)
            return payload
        time.sleep(args.interval)
    raise SystemExit(f"task timed out after {args.timeout}s: {task_id}")


def download(args):
    base, token, model, endpoint = config(args)
    result = poll(args) if args.wait else None
    if result:
        direct = result.get("video_url") or (result.get("metadata") or {}).get("url")
    else:
        direct = None
    if direct:
        url = direct
        headers = {"Authorization": f"Bearer {token}"}
    else:
        url = f"{base}/v1/videos/{urllib.parse.quote(args.task_id)}/content"
        headers = {"Authorization": f"Bearer {token}"}
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=180) as response, open(args.out, "wb") as output:
            output.write(response.read())
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"download failed HTTP {exc.code}") from exc
    print(args.out)


def generate(args):
    args.task_id = create(args)
    result = poll(args, args.task_id)
    args.wait = False
    download(args)


def models(args):
    base, token, _, _ = config(args)
    status, payload = request_json("GET", base + "/v1/models", token)
    check(status, payload)
    for item in payload.get("data", []):
        print(item.get("id", item))


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", help="model id")
    parser.add_argument("--endpoint", choices=["auto", "videos", "generations"])
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--model")
    common.add_argument("--endpoint", choices=["auto", "videos", "generations"])
    common.add_argument("--prompt", required=True)
    common.add_argument("--seconds", type=int, default=4)
    common.add_argument("--resolution", default="480p")
    common.add_argument("--aspect-ratio", default="16:9")
    common.add_argument("--generate-audio", action="store_true")
    common.add_argument("--negative-prompt")
    common.add_argument("--seed", type=int)
    common.add_argument("--reference", dest="references", action="append", help="type=image role=reference source=https://...")

    create_parser = sub.add_parser("create", parents=[common])
    create_parser.set_defaults(func=create)
    generate_parser = sub.add_parser("generate", parents=[common])
    generate_parser.add_argument("--out", default="output.mp4")
    generate_parser.add_argument("--interval", type=int, default=4)
    generate_parser.add_argument("--timeout", type=int, default=900)
    generate_parser.set_defaults(func=generate)

    wait_parser = sub.add_parser("wait")
    wait_parser.add_argument("--task-id", required=True)
    wait_parser.add_argument("--model")
    wait_parser.add_argument("--endpoint", choices=["auto", "videos", "generations"])
    wait_parser.add_argument("--interval", type=int, default=4)
    wait_parser.add_argument("--timeout", type=int, default=900)
    wait_parser.set_defaults(func=poll)

    download_parser = sub.add_parser("download")
    download_parser.add_argument("--task-id", required=True)
    download_parser.add_argument("--model")
    download_parser.add_argument("--endpoint", choices=["auto", "videos", "generations"])
    download_parser.add_argument("--out", default="output.mp4")
    download_parser.add_argument("--wait", action="store_true")
    download_parser.add_argument("--interval", type=int, default=4)
    download_parser.add_argument("--timeout", type=int, default=900)
    download_parser.set_defaults(func=download)
    models_parser = sub.add_parser("models")
    models_parser.add_argument("--model")
    models_parser.add_argument("--endpoint", choices=["auto", "videos", "generations"])
    models_parser.set_defaults(func=models)
    return parser


if __name__ == "__main__":
    load_env()
    args = build_parser().parse_args()
    args.func(args)
