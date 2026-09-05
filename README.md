# seedance-agent-skill

通过用户自定义的 New API 兼容网关生成视频的 Codex skill。仓库不包含任何厂商默认地址或 API 密钥，CLI 使用 Python 标准库，无需安装第三方包。

<p align="center">
  <a href="README.md"><strong>中文</strong></a> |
  <a href="README_EN.md">English</a>
</p>

## 功能

- 支持网关 A 系列 Seedance 2.0/2.5 模型和 Drama Video V2。
- 支持文生视频、参考图片/视频/音频、任务轮询和 MP4 下载。
- 自动识别 `/v1/videos` 与 `/v1/video/generations` 接口，也可以手动指定。
- CLI 输出支持中文和英文，每次运行只显示一种语言。

## 在 Codex 中安装

把下面的提示词发给 Codex：

```text
从 https://github.com/wannds/seedance-agent-skill 安装 Codex skill。克隆仓库，将仓库内容复制到本地 skills 目录的 drama-video-generation 文件夹，将 .env.example 复制为 .env；如果未提供配置，询问我 DRAMA_BASE_URL、DRAMA_API_KEY 和 DRAMA_MODEL。网关地址、模型和 API 密钥由用户自行填写，不要写入任何厂商默认值。Seedance 2.0 只允许使用以 -0826 结尾的模型 ID，禁止使用其他 Seedance 2.0 型号。API 密钥只能保存在 .env，绝不要提交。运行 python scripts/drama_video.py --lang zh --help 验证安装，并确认安装路径。
```

也可以使用 Codex 内置安装脚本：

```powershell
python "$env:USERPROFILE\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" `
  --repo wannds/seedance-agent-skill `
  --path .
```

## 配置

在安装后的 skill 目录中执行：

```powershell
Copy-Item .env.example .env
```

然后编辑 `.env`：

```env
DRAMA_BASE_URL=你的网关根地址
DRAMA_API_KEY=你的API密钥
DRAMA_MODEL=seedance2.5-A
DRAMA_ENDPOINT=auto
DRAMA_LANG=zh
```

`DRAMA_BASE_URL` 填网关根地址，不要带 `/v1`；CLI 会根据模型自动选择接口。当前网关的 A 系列模型（如 `seedance2.5-A`、`seedance2.0-A`）使用 `/v1/videos`；旧式 `*-0826` 模型使用 generations 接口。`.env` 已加入 `.gitignore`，不要提交密钥。

## 语言切换

每次运行选择一种输出语言，不会中英文混排：

```powershell
python scripts/drama_video.py --lang zh generate --prompt "深空中的黑洞与旋转吸积盘" --seconds 4 --resolution 480p --out outputs/black-hole.mp4
python scripts/drama_video.py --lang en generate --prompt "A black hole with a rotating accretion disk in deep space" --seconds 4 --resolution 480p --out outputs/black-hole-en.mp4
```

也可以在 `.env` 中设置默认语言：

```env
DRAMA_LANG=zh
```

命令行的 `--lang en` 或 `--lang zh` 会覆盖 `.env` 中的默认值。

## 生成视频

```powershell
python scripts/drama_video.py --lang zh generate `
  --prompt "电影级科幻风格的黑洞，发光吸积盘，镜头缓慢推进" `
  --model seedance2.5-A `
  --seconds 4 `
  --resolution 480p `
  --aspect-ratio 16:9 `
  --generate-audio `
  --out outputs/black-hole.mp4
```

命令会创建任务、等待完成并下载 MP4。模型 ID 必须使用 `models` 命令返回的值，具体可用模型和价格由网关账户决定。

## 分步操作

```powershell
python scripts/drama_video.py --lang zh models
python scripts/drama_video.py --lang zh create --prompt "..." --seconds 4 --resolution 720p
python scripts/drama_video.py --lang zh wait --task-id TASK_ID --interval 4
python scripts/drama_video.py --lang zh download --task-id TASK_ID --out result.mp4
```

## 接口和时长约束

- 当前网关的 `seedance2.0-A`、`seedance2.5-A` 使用 `POST /v1/videos`。
- 旧式以 `-0826` 结尾的模型才使用 `POST /v1/video/generations`。
- `seedance2.0-A` 通常支持 4-15 秒；`seedance2.5-A` 通常支持 4-30 秒，分辨率以网关返回为准。
- 如果需要精确 3 秒，先生成供应商允许的最短时长，再使用 FFmpeg 本地裁剪。

## 参考素材

使用公开 HTTPS 素材时，可重复传入 `--reference`，格式如下：

```text
--reference "type=image role=reference source=https://example.com/image.jpg"
```

并在提示词中用 `@image1`、`@video1` 或 `@audio1` 指代素材，具体别名以网关文档为准。

## 许可证

MIT。网关账户、模型权限、计费和生成媒体遵循用户所选服务商的条款。
