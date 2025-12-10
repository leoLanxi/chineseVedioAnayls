# Chinese Video ASR

**概述**
- 遍历 `input_videos`，提取中文对白并生成 `outputs/<原文件名>/<原文件名>.docx` 与 `outputs/<原文件名>/<原文件名>.srt`。
- 文本规则：保留中文对白，轻度口语清理与断句，Word 为自然段，SRT 保留时间码并适配中文分行。

**使用模型**
- ASR：`paraformer-zh`（ModelScope 路径：`iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch`）
- VAD：`fsmn-vad`（ModelScope 路径：`iic/speech_fsmn_vad_zh-cn-16k-common-pytorch`）
- 标点：`ct-punc`（ModelScope 路径：`iic/punc_ct-transformer_cn-en-common-vocab471067-large`）
- 入口：`funasr.AutoModel`，代码位置 `process_videos.py:44-48`

**资源占用（参考）**
- 磁盘缓存（模型与词典）：约 2.1–2.5 GB（ASR ~944 MB；Punc ~1.05 GB；附加词典与配置若干十 MB）。
- 运行内存（CPU 推理）：通常 2–5 GB（按视频时长与并发变化）；16 GB RAM 运行稳定。
- GPU（可选，Windows/CUDA）：建议显存 ≥6 GB 以获得稳定吞吐（本仓库默认 CPU）。

**平台与安装**
- macOS（Apple Silicon）：
  - 一键：`bash scripts/setup_mac.sh`
  - 功能：创建 `.venv` 并安装依赖；如缺失尝试 `brew install ffmpeg`；设置模型缓存并预拉取。
- Windows 11（D 盘约束）：
  - 一键：`PowerShell -ExecutionPolicy Bypass -File scripts/setup_win.ps1`
  - 落地位置：虚拟环境 `D:\chineseVedioAnayls\.venv`；`ffmpeg` 在 `D:\tools\ffmpeg`；模型缓存 `D:\modelscope_cache`。
  - 本脚本不向 C 盘写入任何拉取内容。

**运行**
- 将视频放入 `input_videos`（可含子文件夹，支持 `mp4/mov/mkv/avi/mp3/wav/m4a`）。
- 执行：`python3 process_videos.py`
- 完成日志：`完成: <原文件名> -> outputs/<原文件名>/`

**输出说明**
- Word（`.docx`）：自然段落，未包含时间戳，来源于识别与整理后的中文句子（`process_videos.py:116-122`）。
- SRT（`.srt`）：保留精准时间码；若模型未返回时间戳，按整段音频时长为句子比例分配（`process_videos.py:100-115`）。

**仓库与分支**
- 推送脚本：`bash scripts/setup_repo.sh <remote-url>`（默认远程：`https://github.com/leoLanxi/chineseVedioAnayls.git`）。
- 分支策略：`win11` 为主分支；`macos` 为次分支。

**创作者**
- 作者：`leoLanxi`
- 项目维护：`leoLanxi`（与协作开发者）

**关键文件**
- 处理主逻辑：`process_videos.py`
- 文本整理与字幕构建：`cn_asr/formatter.py`
- 预拉取模型：`scripts/prefetch_models.py`
- 安装脚本：`scripts/setup_mac.sh`、`scripts/setup_win.ps1`

