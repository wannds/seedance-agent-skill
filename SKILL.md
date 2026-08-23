---
name: drama-video-generation
description: Generate videos through a user-configured New API gateway. Supports Seedance 2.0/2.5, Drama Video V2, 0826 models, references, polling, and MP4 download.
metadata:
  short-description: New API video generation
---

# Drama Video Generation

Use the bundled zero-dependency CLI for video generation. It reads `DRAMA_BASE_URL`, `DRAMA_API_KEY`, `DRAMA_MODEL`, and `DRAMA_ENDPOINT` from `.env` in the skill directory or the process environment.

## Quick Start

```powershell
python scripts/drama_video.py generate `
  --prompt "A cinematic black hole with a glowing accretion disk, slow camera push-in" `
  --model seedance-2.0-fast `
  --seconds 4 `
  --resolution 480p `
  --aspect-ratio 16:9 `
  --generate-audio `
  --out outputs/black-hole.mp4
```

The command creates the task, polls until `completed` or `failed`, and downloads the MP4. Save the returned task id when using the separate subcommands.

## Model Routing

- `seedance2.0`, `seedance2.5`, `drama-video-v2`, and their non-0826 variants use `POST /v1/videos`.
- `seedance-2.0-0826` and `seedance-2.0-fast-0826` use `POST /v1/video/generations`, with polling at `/v1/video/generations/{task_id}`.
- `DRAMA_ENDPOINT=auto` selects the route from the model name. Use `--endpoint videos` or `--endpoint generations` to override.
- Always use the model ids returned by `GET /v1/models` for the configured token. Model availability and pricing are group-specific.

## Constraints

- Seedance 2.0: 4-15 seconds; 480p, 720p, 1080p, or 4K.
- Seedance 2.5: 4-30 seconds; 480p or 720p.
- Drama Video V2: 5, 10, or 15 seconds; fast supports up to 720p, standard supports 1080p.
- 0826 models: 4-15 seconds; fast supports up to 720p.
- Use `--reference type=... role=... source=...` for public HTTPS reference media. Each reference should be named in the prompt as `@image1`, `@video1`, or `@audio1` (or the provider's documented localized aliases) when using the Seedance 2.0/2.5 reference contract.
- Do not use a 3-second request. Generate the provider minimum (usually 4 seconds) and trim locally with FFmpeg if an exact 3-second output is required.

## Separate Operations

```powershell
python scripts/drama_video.py models
python scripts/drama_video.py create --prompt "..." --seconds 4 --resolution 720p
python scripts/drama_video.py wait --task-id TASK_ID --interval 4
python scripts/drama_video.py download --task-id TASK_ID --out result.mp4
```

The download command first uses `video_url` or `metadata.url` when returned; otherwise it requests `/v1/videos/{task_id}/content` with the Bearer token.
