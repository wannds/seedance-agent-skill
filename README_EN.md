# seedance-agent-skill

A Codex skill for generating videos through a user-configured New API-compatible gateway. The repository contains no provider default URL or API key, and its CLI uses only the Python standard library.

<p align="center">
  <a href="README.md">中文</a> |
  <a href="README_EN.md"><strong>English</strong></a>
</p>

## Features

- Supports Seedance 2.0 only with `-0826` model ids, plus Seedance 2.5 and Drama Video V2.
- Supports text-to-video, image/video/audio references, task polling, and MP4 downloads.
- Selects `/v1/videos` or `/v1/video/generations` automatically, with a manual override.
- CLI output is available in Chinese or English; each run uses one language only.

## Install In Codex

Give Codex this prompt:

```text
Install the Codex skill from https://github.com/wannds/seedance-agent-skill. Clone the repository, copy its contents into the local skills directory as drama-video-generation, and copy .env.example to .env. If configuration is not supplied, ask me for DRAMA_BASE_URL, DRAMA_API_KEY, and DRAMA_MODEL. The user supplies the gateway, model, and API key; do not insert provider defaults. Seedance 2.0 permits only model ids ending in -0826; reject every other Seedance 2.0 model. Keep the API key only in .env and never commit it. Run python scripts/drama_video.py --lang en --help to validate the installation and confirm the installed path.
```

The built-in installer helper can also install the repository:

```powershell
python "$env:USERPROFILE\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" `
  --repo wannds/seedance-agent-skill `
  --path .
```

## Configuration

From the installed skill directory, create the local environment file:

```powershell
Copy-Item .env.example .env
```

Then edit `.env`:

```env
DRAMA_BASE_URL=YOUR_GATEWAY_ORIGIN
DRAMA_API_KEY=YOUR_API_KEY
DRAMA_MODEL=seedance-2.0-fast-0826
DRAMA_ENDPOINT=auto
DRAMA_LANG=en
```

Set `DRAMA_BASE_URL` to the gateway origin without `/v1`; the CLI selects the route from the model. Seedance 2.0 permits only ids such as `seedance-2.0-0826` and `seedance-2.0-fast-0826` that end in `-0826`, and always uses the generations endpoint. Other supported families such as Seedance 2.5 use the videos endpoint. `.env` is ignored by Git; never commit credentials.

## Language Selection

Choose one output language per run; Chinese and English are not mixed:

```powershell
python scripts/drama_video.py --lang en generate --prompt "A black hole with a rotating accretion disk in deep space" --seconds 4 --resolution 480p --out outputs/black-hole-en.mp4
python scripts/drama_video.py --lang zh generate --prompt "深空中的黑洞与旋转吸积盘" --seconds 4 --resolution 480p --out outputs/black-hole.mp4
```

Set a default language in `.env` when preferred:

```env
DRAMA_LANG=en
```

The command-line `--lang en` or `--lang zh` flag overrides the `.env` default.

## Generate A Video

```powershell
python scripts/drama_video.py --lang en generate `
  --prompt "A cinematic black hole with a glowing accretion disk, slow camera push-in" `
  --model seedance-2.0-fast-0826 `
  --seconds 4 `
  --resolution 480p `
  --aspect-ratio 16:9 `
  --generate-audio `
  --out outputs/black-hole.mp4
```

The command creates the task, waits for completion, and downloads the MP4. Use a model ID returned by `models`; availability and pricing depend on the configured gateway account.

## Separate Operations

```powershell
python scripts/drama_video.py --lang en models
python scripts/drama_video.py --lang en create --prompt "..." --seconds 4 --resolution 720p
python scripts/drama_video.py --lang en wait --task-id TASK_ID --interval 4
python scripts/drama_video.py --lang en download --task-id TASK_ID --out result.mp4
```

## Endpoints And Duration Constraints

- Seedance 2.0 permits only ids such as `seedance-2.0-0826` and `seedance-2.0-fast-0826` that end in `-0826`; they use `POST /v1/video/generations`.
- The CLI rejects `seedance-2.0`, `seedance-2.0-fast`, and any other Seedance 2.0 id without the `-0826` suffix. The `models` command hides them as well.
- Other supported families such as Seedance 2.5 and Drama Video V2 use `POST /v1/videos`.
- Seedance 2.0 `*-0826` models usually accept 4-15 seconds; fast variants support up to 720p. Seedance 2.5 usually accepts 4-30 seconds, with resolutions determined by the gateway.
- For an exact 3-second file, generate the provider minimum first, then trim locally with FFmpeg.

## Reference Media

For public HTTPS media, pass `--reference` more than once as needed:

```text
--reference "type=image role=reference source=https://example.com/image.jpg"
```

Mention the asset in the prompt as `@image1`, `@video1`, or `@audio1`; follow the gateway documentation for localized aliases.

## License

MIT. The gateway account, model access, pricing, and generated media remain subject to the terms of the service provider selected by the user.
