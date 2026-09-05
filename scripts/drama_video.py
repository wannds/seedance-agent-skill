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
LANG = "en"
DEFAULT_MODEL = "seedance2.5-A"


def text(en, zh):
    return zh if LANG == "zh" else en


def selected_language(argv=None):
    argv = argv or sys.argv[1:]
    for index, value in enumerate(argv):
        if value == "--lang" and index + 1 < len(argv):
            return argv[index + 1]
        if value.startswith("--lang="):
            return value.split("=", 1)[1]
    return os.environ.get("DRAMA_LANG", "en")


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


def is_seedance_20(model):
    """Return True for the legacy *-0826 route, not the A-series /v1/videos route."""
    normalized = model.strip().lower().replace("-", "")
    return normalized.startswith("seedance2.0") and not model.strip().lower().endswith("-a")


def validate_model(model, endpoint="auto"):
    if not is_seedance_20(model):
        return
    if not model.strip().lower().endswith("-0826"):
        raise SystemExit(text(
            f"Seedance 2.0 model is disabled unless its id ends with -0826: {model}",
            f"Seedance 2.0 模型必须使用以 -0826 结尾的 ID，已禁止：{model}",
        ))
    if endpoint == "videos":
        raise SystemExit(text(
            "Seedance 2.0 *-0826 models require the generations endpoint",
            "Seedance 2.0 的 *-0826 模型必须使用 generations 接口",
        ))


def model_is_allowed(model):
    return not is_seedance_20(model) or model.strip().lower().endswith("-0826")


def config(args):
    base = (os.environ.get("DRAMA_BASE_URL") or "").rstrip("/")
    if not base:
        raise SystemExit(text("DRAMA_BASE_URL is missing; set the user's gateway origin in .env or the environment", "缺少 DRAMA_BASE_URL；请在 .env 或环境变量中填写用户网关根地址"))
    token = os.environ.get("DRAMA_API_KEY")
    if not token:
        raise SystemExit(text("DRAMA_API_KEY is missing; set it in .env or the environment", "缺少 DRAMA_API_KEY；请在 .env 或环境变量中填写用户 API 密钥"))
    model = args.model or os.environ.get("DRAMA_MODEL", DEFAULT_MODEL)
    endpoint = args.endpoint or os.environ.get("DRAMA_ENDPOINT", "auto")
    validate_model(model, endpoint)
    if endpoint == "auto":
        endpoint = "generations" if is_seedance_20(model) else "videos"
    if endpoint not in {"videos", "generations"}:
        raise SystemExit(text("DRAMA_ENDPOINT must be auto, videos, or generations", "DRAMA_ENDPOINT 必须是 auto、videos 或 generations"))
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
        raise SystemExit(text(f"network error: {exc}", f"网络错误：{exc}")) from exc


def check(status, payload):
    if status >= 400:
        raise SystemExit(text(f"HTTP {status}: {json.dumps(payload, ensure_ascii=False)}", f"HTTP 错误 {status}：{json.dumps(payload, ensure_ascii=False)}"))


def create_payload(args, model, endpoint):
    payload = {
        "model": model,
        "prompt": args.prompt,
        "seconds": args.seconds,
        "resolution": args.resolution,
        "aspect_ratio": args.aspect_ratio,
    }
    if endpoint == "videos":
        payload["task_mode"] = "references" if args.references else "text"
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
            raise SystemExit(text(f"reference needs type= role= source=: {value}", f"参考素材必须包含 type=、role=、source=：{value}"))
    return {"type": fields["type"], "role": fields["role"], "source": fields["source"]}


def create(args):
    base, token, model, endpoint = config(args)
    path = "/v1/video/generations" if endpoint == "generations" else "/v1/videos"
    status, payload = request_json("POST", base + path, token, create_payload(args, model, endpoint))
    check(status, payload)
    task_id = payload.get("id") or payload.get("task_id")
    if not task_id:
        raise SystemExit(text(f"create response has no task id: {payload}", f"创建响应没有任务 ID：{payload}"))
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
    raise SystemExit(text(f"task timed out after {args.timeout}s: {task_id}", f"任务超时（{args.timeout} 秒）：{task_id}"))


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
        raise SystemExit(text(f"download failed HTTP {exc.code}", f"下载失败，HTTP {exc.code}")) from exc
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
        model = item.get("id", item) if isinstance(item, dict) else item
        if isinstance(model, str) and model_is_allowed(model):
            print(model)


def build_parser():
    parser = argparse.ArgumentParser(description=text("Zero-dependency video CLI", "零依赖视频生成 CLI"))
    parser.add_argument("--model", help=text("model id", "模型 ID"))
    parser.add_argument("--endpoint", choices=["auto", "videos", "generations"], help=text("API endpoint mode", "API 端点模式"))
    parser.add_argument("--lang", choices=["en", "zh"], default=LANG, help=text("output language", "输出语言"))
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--model")
    common.add_argument("--endpoint", choices=["auto", "videos", "generations"])
    common.add_argument("--lang", choices=["en", "zh"], default=argparse.SUPPRESS, help=text("output language", "输出语言"))
    common.add_argument("--prompt", required=True, help=text("video prompt", "视频提示词"))
    common.add_argument("--seconds", type=int, default=4, help=text("duration in seconds", "时长（秒）"))
    common.add_argument("--resolution", default="480p", help=text("resolution", "分辨率"))
    common.add_argument("--aspect-ratio", default="16:9", help=text("aspect ratio", "画面比例"))
    common.add_argument("--generate-audio", action="store_true", help=text("request audio", "请求生成音频"))
    common.add_argument("--negative-prompt", help=text("negative prompt", "负面提示词"))
    common.add_argument("--seed", type=int, help=text("random seed", "随机种子"))
    common.add_argument("--reference", dest="references", action="append", help=text("type=image role=reference source=https://...", "type=image role=reference source=https://..."))

    create_parser = sub.add_parser("create", parents=[common], help=text("create a task", "创建任务"))
    create_parser.set_defaults(func=create)
    generate_parser = sub.add_parser("generate", parents=[common], help=text("create, poll, and download", "创建、轮询并下载"))
    generate_parser.add_argument("--out", default="output.mp4", help=text("output MP4 path", "输出 MP4 路径"))
    generate_parser.add_argument("--interval", type=int, default=4, help=text("poll interval", "轮询间隔"))
    generate_parser.add_argument("--timeout", type=int, default=900, help=text("timeout in seconds", "超时秒数"))
    generate_parser.set_defaults(func=generate)

    wait_parser = sub.add_parser("wait", help=text("poll a task", "轮询任务"))
    wait_parser.add_argument("--task-id", required=True, help=text("task ID", "任务 ID"))
    wait_parser.add_argument("--model")
    wait_parser.add_argument("--endpoint", choices=["auto", "videos", "generations"])
    wait_parser.add_argument("--lang", choices=["en", "zh"], default=argparse.SUPPRESS, help=text("output language", "输出语言"))
    wait_parser.add_argument("--interval", type=int, default=4)
    wait_parser.add_argument("--timeout", type=int, default=900)
    wait_parser.set_defaults(func=poll)

    download_parser = sub.add_parser("download", help=text("download a completed task", "下载已完成任务"))
    download_parser.add_argument("--task-id", required=True, help=text("task ID", "任务 ID"))
    download_parser.add_argument("--model")
    download_parser.add_argument("--endpoint", choices=["auto", "videos", "generations"])
    download_parser.add_argument("--lang", choices=["en", "zh"], default=argparse.SUPPRESS, help=text("output language", "输出语言"))
    download_parser.add_argument("--out", default="output.mp4", help=text("output MP4 path", "输出 MP4 路径"))
    download_parser.add_argument("--wait", action="store_true")
    download_parser.add_argument("--interval", type=int, default=4)
    download_parser.add_argument("--timeout", type=int, default=900)
    download_parser.set_defaults(func=download)
    models_parser = sub.add_parser("models", help=text("list available models", "列出可用模型"))
    models_parser.add_argument("--model")
    models_parser.add_argument("--endpoint", choices=["auto", "videos", "generations"])
    models_parser.add_argument("--lang", choices=["en", "zh"], default=argparse.SUPPRESS, help=text("output language", "输出语言"))
    models_parser.set_defaults(func=models)
    return parser


if __name__ == "__main__":
    load_env()
    LANG = selected_language()
    args = build_parser().parse_args()
    LANG = getattr(args, "lang", LANG)
    args.func(args)
