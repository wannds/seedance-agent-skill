---
name: drama-video-generation
description: Generate videos through a user-configured New API gateway using Seedance A-series models only. Supports the documented JSON /v1/videos contract, references, polling, and MP4 download.
metadata:
  short-description: New API video generation
---

# Seedance Video Generation

Use the bundled zero-dependency CLI for Seedance A-series video generation. It reads `DRAMA_BASE_URL`, `DRAMA_API_KEY`, and `DRAMA_MODEL` from `.env` in the skill directory or the process environment. Non-Seedance and `0826` models are filtered from discovery and rejected before submission.

Set `DRAMA_LANG=en` or `DRAMA_LANG=zh` for the default CLI language. A per-run `--lang en` or `--lang zh` flag overrides the environment setting; each run uses one language only.

## Quick Start

```powershell
python scripts/drama_video.py generate `
  --prompt "A cinematic black hole with a glowing accretion disk, slow camera push-in" `
  --model seedance2.5-A `
  --seconds 4 `
  --resolution 480p `
  --aspect-ratio 16:9 `
  --out outputs/black-hole.mp4
```

The command creates the task, polls until `completed` or `failed`, and downloads the MP4. Save the returned task id when using the separate subcommands.

## Seedance Model Selection

- A-series models such as `seedance2.5-A`, `seedance2.0-A`, and `seedance2.0-fast-A` use JSON `POST /v1/videos`.
- Model ids containing `0826` are excluded and are never submitted.
- The `models` command prints only non-`0826` model ids beginning with `seedance`; use ids returned by `GET /v1/models` for the configured token.
- Always use the model ids returned by `GET /v1/models` for the configured token. Model availability and pricing are group-specific.

## Constraints

- Seedance 2.0: 4-15 seconds; 480p, 720p, 1080p, or 4K where the model permits.
- Seedance 2.5: 4-30 seconds; 480p, 720p, or 1080p.
- A-series references use `--reference type=... role=... source=...` with public HTTPS URLs or Data URIs. Mention each reference in the prompt using the documented `@图N`/`@视频N`/`@音频N` aliases (or the gateway's accepted localized aliases).
- For A-series requests, the CLI sends only the documented public fields: `model`, `prompt`, `seconds`, `resolution`, `aspect_ratio`, and `references`.
- Do not use a 3-second request. Generate the provider minimum (usually 4 seconds) and trim locally with FFmpeg if an exact 3-second output is required.

## Separate Operations

```powershell
python scripts/drama_video.py models
python scripts/drama_video.py create --prompt "..." --seconds 4 --resolution 720p
python scripts/drama_video.py wait --task-id TASK_ID --interval 4
python scripts/drama_video.py download --task-id TASK_ID --out result.mp4
```

The download command always requests `/v1/videos/{task_id}/content` with the Bearer token after the task is completed. This keeps downloads on the New API proxy instead of depending on an upstream URL.
