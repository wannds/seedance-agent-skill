# seedance-agent-skill

这是一个通过用户配置的 New API 兼容网关生成视频的 Codex skill，CLI 不依赖第三方 Python 包。

## 安装

把仓库内容复制到 `$CODEX_HOME/skills/drama-video-generation`，将 `.env.example` 复制为 `.env`，再填写：

```env
DRAMA_BASE_URL=你的网关根地址
DRAMA_API_KEY=你的API密钥
DRAMA_MODEL=seedance-2.0-fast
DRAMA_ENDPOINT=auto
DRAMA_LANG=zh
```

不要提交 `.env` 或 API 密钥。

## 生成视频

```powershell
python scripts/drama_video.py --lang zh generate `
  --prompt "深空中的黑洞与旋转吸积盘，电影级科幻质感" `
  --seconds 4 `
  --resolution 480p `
  --aspect-ratio 16:9 `
  --generate-audio `
  --out outputs/black-hole.mp4
```

`--lang zh` 输出中文；`--lang en` 输出英文。也可以使用 `.env` 中的 `DRAMA_LANG=zh` 或 `DRAMA_LANG=en`。

## 分步操作

```powershell
python scripts/drama_video.py --lang zh models
python scripts/drama_video.py --lang zh create --prompt "..." --seconds 4 --resolution 720p
python scripts/drama_video.py --lang zh wait --task-id TASK_ID --interval 4
python scripts/drama_video.py --lang zh download --task-id TASK_ID --out result.mp4
```

支持 Seedance 2.0 / 2.5、Drama Video V2、0826 模型、参考图片/视频/音频、轮询和 MP4 下载。
