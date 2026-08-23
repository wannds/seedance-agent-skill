# One-shot install prompt

```text
Install the Codex skill from https://github.com/wannds/seedance-agent-skill. Clone the repository, copy the repository contents into $CODEX_HOME/skills/drama-video-generation, copy .env.example to .env, and ask me for DRAMA_BASE_URL and DRAMA_API_KEY if they are not already supplied. The user chooses the gateway and token; do not insert a provider default. Keep the API key only in .env and never commit it. Run `python scripts/drama_video.py --help` and, after the user fills the configuration, `python scripts/drama_video.py models` to validate the installation, then confirm the installed path and available models.
从 https://github.com/wannds/seedance-agent-skill 安装 Codex skill。克隆仓库，将内容复制到 `$CODEX_HOME/skills/drama-video-generation`，将 `.env.example` 复制为 `.env`；如果未提供配置，询问 `DRAMA_BASE_URL` 和 `DRAMA_API_KEY`。网关和令牌由用户自行选择，不要填入任何厂商默认值。API 密钥只能保存在 `.env`，不要提交。运行 `python scripts/drama_video.py --help`；用户填写配置后运行 `python scripts/drama_video.py models` 验证，并确认安装路径和可用模型。
```
