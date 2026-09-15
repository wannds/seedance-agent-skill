---
name: drama-video-generation
description: Generate Seedance A-series videos through a user-configured downstream NewAPI gateway. Supports text prompts, local image/video/audio upload, visual-reference prompt construction, task polling, and MP4 download.
metadata:
  short-description: Downstream Seedance video gateway
---

# Downstream Seedance Video

Use this skill as a client of a user's NewAPI-compatible downstream gateway. The gateway is the only API endpoint the user needs to expose to the agent. Never assume a provider URL, API key, model, upload token, or storage URL.

## Configuration

Read these values from `.env` in the skill directory or process environment:

```env
DRAMA_BASE_URL=https://your-newapi.example.com
DRAMA_API_KEY=your-newapi-user-token
DRAMA_MODEL=seedance2.5-A
# Optional. If omitted, the skill uses DRAMA_BASE_URL/v1/media/upload
# with DRAMA_API_KEY.
DRAMA_UPLOAD_URL=https://your-newapi.example.com/v1/media/upload
DRAMA_UPLOAD_KEY=your-media-upload-token
DRAMA_LANG=zh
```

`DRAMA_BASE_URL` must be the gateway origin without `/v1`. For local files, the skill uploads over HTTPS to `DRAMA_UPLOAD_URL`; when it is omitted, it derives `${DRAMA_BASE_URL}/v1/media/upload` and reuses `DRAMA_API_KEY`. The gateway must expose that multipart endpoint and return `{ "url": "https://..." }`. Keep secrets local and never print or commit them.

Before creating a task, call `GET /v1/models` and select only a returned model whose id starts with `seedance` and ends with `-A`. Respect the user's configured model if it is present in the returned list; otherwise explain the mismatch and ask for a valid model.

## User Intent And Prompt Construction

When the user provides an image, first inspect it as a visual reference. Treat a character turnaround or three-view sheet as an identity sheet, not as a scene to reproduce literally.

Construct a concise video prompt with these parts, in order:

1. **Subject lock:** preserve the referenced character's face, hairstyle, clothing, colors, accessories, proportions, and rendering style.
2. **Action:** describe one physically coherent action with a clear start, middle, and end.
3. **Camera:** state framing and camera motion only when useful; default to a stable medium shot.
4. **Motion details:** describe natural hair, fabric, and accessory movement without inventing extra characters.
5. **Continuity constraints:** request stable identity, hands, face, clothing, lighting, and background; forbid text, watermark, duplicate limbs, and unintended subjects.

For a three-view sheet, do not ask the model to animate all three panels. Say that the sheet is the sole appearance reference and request one consistent character in the generated shot.

Prefer safe, concrete actions such as turning around, waving, walking, looking toward camera, or a short game-style idle animation. Do not add romantic or sexual behavior unless the user explicitly requests it and the request is allowed by the provider. If the provider rejects a prompt or reference, do not retry unchanged; explain the rejection and suggest a less ambiguous action or reference.

## References

For an existing HTTPS reference, pass:

```text
--reference "type=image role=reference source=https://example.com/reference.png"
```

For a local file, configure `DRAMA_UPLOAD_URL` and `DRAMA_UPLOAD_KEY`, then pass:

```text
--reference-file "type=image path=reference.png"
--reference-file "type=video path=motion.mp4"
--reference-file "type=audio path=voice.mp3"
```

The CLI uploads the file first and uses the returned HTTPS URL in `references`. Every reference should be mentioned in the prompt with the gateway's accepted aliases, for example `@图1`, `@视频1`, or `@音频1`.

Do not send local paths, raw Base64, or Data URIs unless the configured gateway explicitly supports them. The downstream upload service may accept larger files than a specific model can use; the model's own limits still apply at task creation.

## API Workflow

1. Discover models with `GET /v1/models`.
2. Upload local references, if any, with `DRAMA_UPLOAD_URL`.
3. Create a task with JSON `POST /v1/videos`.
4. Save the public `id` from the response.
5. Poll `GET /v1/videos/{id}` every 3–5 seconds.
6. Download only after `status` is `completed` using `GET /v1/videos/{id}/content`.

Never use an upstream vendor URL, upstream key, internal task id, or metadata URL. Do not repeat `POST /v1/videos` after a timeout until the task state has been checked, because creation is not idempotent.

## Supported Public Fields

Send only the documented fields:

```json
{
  "model": "seedance2.5-A",
  "prompt": "...",
  "seconds": 4,
  "resolution": "480p",
  "aspect_ratio": "16:9",
  "references": []
}
```

Use 4–15 seconds for Seedance 2.0 and 4–30 seconds for Seedance 2.5, subject to the model list and gateway validation. Do not invent unsupported fields or silently downgrade a user's requested resolution.

## CLI

```powershell
python scripts/drama_video.py models
python scripts/drama_video.py generate --prompt "角色原地转一圈" --seconds 4 --resolution 480p --out output.mp4
python scripts/drama_video.py generate --prompt "参考@图1中的角色原地转一圈" --reference-file "type=image path=reference.png" --seconds 4 --resolution 480p --out output.mp4
```

The CLI is zero-dependency and uses only the Python standard library.
