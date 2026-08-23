# seedance-agent-skill

Codex skill and zero-dependency Python CLI for a New API compatible video gateway.
通过 New API 兼容网关生成视频的 Codex skill，CLI 零依赖。

## Install In Codex / 在 Codex 中安装

After pushing this folder to GitHub, give an agent this prompt:

```text
Install the Codex skill from https://github.com/wannds/seedance-agent-skill. Clone the repository, copy the repository contents into the local skills directory as drama-video-generation, copy .env.example to .env, and ask me for DRAMA_BASE_URL and DRAMA_API_KEY if they are not already supplied. Do not commit .env or any API key. Validate the skill with its CLI --help command and confirm the installed path.
从 https://github.com/wannds/seedance-agent-skill 安装 Codex skill。克隆仓库，将内容复制到本地 skills 目录并命名为 drama-video-generation，将 .env.example 复制为 .env；如果未提供配置，向我询问 DRAMA_BASE_URL 和 DRAMA_API_KEY。不要提交 .env 或任何 API 密钥。运行 CLI 的 --help 验证安装并确认路径。
```

For a direct repository install using the built-in installer helper:

```powershell
python "$env:USERPROFILE\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" `
  --repo wannds/seedance-agent-skill `
  --path .
```

The CLI itself loads configuration from the installed skill folder's `.env`.

## Configuration / 配置

```powershell
Copy-Item .env.example .env
# edit .env; never commit it
```

`DRAMA_BASE_URL` is required and should be the user's gateway origin without `/v1`. The CLI appends the correct route. `DRAMA_ENDPOINT=auto` is recommended.
必须填写 `DRAMA_BASE_URL`，填写用户自己的网关根地址，不要带 `/v1`；CLI 会自动补全路由。推荐使用 `DRAMA_ENDPOINT=auto`。

## License

MIT. The gateway account, model access, pricing, and generated media remain subject to the provider's terms.
