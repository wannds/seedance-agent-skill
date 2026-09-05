# One-shot Install Prompt

Send the entire prompt below to Codex:

```text
Install the Codex skill from https://github.com/wannds/seedance-agent-skill. Clone the repository, copy its contents into the local skills directory as drama-video-generation, and copy .env.example to .env. If configuration is not supplied, ask me for DRAMA_BASE_URL, DRAMA_API_KEY, and DRAMA_MODEL. Use only Seedance A-series model ids returned by GET /v1/models that do not contain `0826`; all supported models use JSON `/v1/videos`. The user supplies the gateway, model, and API key; do not insert provider defaults. Keep the API key only in .env and never commit it. Run python scripts/drama_video.py --lang en --help to validate the installation and confirm the installed path.
```

English CLI example:

```powershell
python scripts/drama_video.py --lang en generate --prompt "..." --seconds 4 --resolution 720p --out output.mp4
```

Chinese prompt: [INSTALL_PROMPT.md](INSTALL_PROMPT.md)
