# 一键安装提示词

将下面整段提示词发送给 Codex：

```text
从 https://github.com/wannds/seedance-agent-skill 安装 Codex skill。克隆仓库，将仓库内容复制到本地 skills 目录的 drama-video-generation 文件夹，将 .env.example 复制为 .env；如果未提供配置，询问我 DRAMA_BASE_URL、DRAMA_API_KEY 和 DRAMA_MODEL。网关地址、模型和 API 密钥由用户自行填写，不要写入任何厂商默认值。Seedance 2.0 只允许使用以 -0826 结尾的模型 ID，禁止使用其他 Seedance 2.0 型号。API 密钥只能保存在 .env，绝不要提交。运行 python scripts/drama_video.py --lang zh --help 验证安装，并确认安装路径。
```

中文 CLI 示例：

```powershell
python scripts/drama_video.py --lang zh generate --prompt "..." --seconds 4 --resolution 720p --out output.mp4
```

英文版提示词：[INSTALL_PROMPT_EN.md](INSTALL_PROMPT_EN.md)
