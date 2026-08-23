# seedance-agent-skill

Codex skill and zero-dependency Python CLI for a New API compatible video gateway.

## Install In Codex

After pushing this folder to GitHub, give an agent this prompt:

```text
Install the Codex skill from https://github.com/wannds/seedance-agent-skill. Clone the repository, copy the repository contents into the local skills directory as drama-video-generation, copy .env.example to .env, and ask me for DRAMA_BASE_URL and DRAMA_API_KEY if they are not already supplied. Do not commit .env or any API key. Validate the skill with its CLI --help command and confirm the installed path.
```

For a direct repository install using the built-in installer helper:

```powershell
python "$env:USERPROFILE\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" `
  --repo wannds/seedance-agent-skill `
  --path .
```

The CLI itself loads configuration from the installed skill folder's `.env`.

## Configuration

```powershell
Copy-Item .env.example .env
# edit .env; never commit it
```

`DRAMA_BASE_URL` is required and should be the user's gateway origin without `/v1`. `DRAMA_ENDPOINT=auto` is recommended. Set `DRAMA_LANG=en` or `DRAMA_LANG=zh` to choose the CLI language; `--lang en` or `--lang zh` overrides the environment value.

## Language

Use one language per run:

```powershell
python scripts/drama_video.py --lang en generate --prompt "..."
python scripts/drama_video.py --lang zh generate --prompt "..."
```

Chinese documentation: [README.zh-CN.md](README.zh-CN.md)

## License

MIT. The gateway account, model access, pricing, and generated media remain subject to the provider's terms.
