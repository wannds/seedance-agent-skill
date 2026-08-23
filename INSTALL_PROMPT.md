# One-shot install prompt

```text
Install the Codex skill from https://github.com/wannds/drama-video-generation-skill. Clone the repository, copy the repository contents into $CODEX_HOME/skills/drama-video-generation, copy .env.example to .env, and ask me for DRAMA_BASE_URL and DRAMA_API_KEY if they are not already supplied. The user chooses the gateway and token; do not insert a provider default. Keep the API key only in .env and never commit it. Run `python scripts/drama_video.py --help` and, after the user fills the configuration, `python scripts/drama_video.py models` to validate the installation, then confirm the installed path and available models.
```
