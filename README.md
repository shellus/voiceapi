# voiceapi - 基于sherpa-onnx的语音转录/合成API

基于 [k2-fsa/sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) 构建的简洁语音API服务。

<img src="./screenshot.jpg" width="60%">

## 项目简介

本项目提供语音识别(ASR)和语音合成(TTS)的WebSocket流式API和HTTP API服务，支持中英文等多语言处理。

## 技术选型

- **后端框架**: FastAPI + uvicorn
- **语音处理**: sherpa-onnx
- **前端**: 原生HTML/JavaScript
- **Python版本**: 3.10+

## 主要目录结构

```
voiceapi/
├── app.py              # 主应用入口
├── voiceapi/           # 核心模块
│   ├── asr.py         # 语音识别模块
│   └── tts.py         # 语音合成模块
├── assets/            # 前端资源
│   ├── index.html     # 演示页面
│   ├── app.js         # 前端逻辑
│   └── audio_process.js # 音频处理
├── examples/          # 示例代码
└── models/           # 模型文件目录(需下载)
```

## 快速开始

### 1. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
# 使用虚拟环境的pip安装，避免系统包管理冲突
./venv/bin/pip install -r requirements.txt -i https://repo.huaweicloud.com/repository/pypi/simple
```

### 3. 下载模型文件

项目需要下载模型文件到 `models` 目录，默认使用的模型：
- ASR模型: `sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20` (中英双语流式)
- TTS模型: `vits-zh-hf-theresa` (中文，804个说话人)

#### 必需的VAD模型
```bash
mkdir -p silero_vad
cd silero_vad
curl -SL -o silero_vad.onnx https://github.com/snakers4/silero-vad/raw/master/src/silero_vad/data/silero_vad.onnx
cd ..
```

#### 默认ASR模型
```bash
curl -SL -O https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20.tar.bz2
tar -xjf sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20.tar.bz2
```

#### 默认TTS模型
```bash
curl -SL -O https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-zh-hf-theresa.tar.bz2
tar -xjf vits-zh-hf-theresa.tar.bz2
```

### 4. 运行应用

```bash
# 使用虚拟环境的Python运行
./venv/bin/python app.py --port 8001
```

访问 `http://localhost:8001/` 查看演示页面

**注意**: 首次运行前必须下载模型文件，否则会出现模型文件不存在的错误。

## 支持的模型

| 模型名称 | 语言支持 | 类型 | 说明 |
|---------|---------|------|------|
| zipformer-bilingual-zh-en-2023-02-20 | 中英文 | 在线ASR | 流式Zipformer双语 |
| sense-voice-zh-en-ja-ko-yue-2024-07-17 | 中英日韩粤 | 离线ASR | SenseVoice多语言 |
| paraformer-trilingual-zh-cantonese-en | 中粤英 | 离线ASR | Paraformer三语 |
| paraformer-en-2024-03-09 | 英文 | 离线ASR | Paraformer英文 |
| vits-zh-hf-theresa | 中文 | TTS | VITS中文，804说话人 |
| melo-tts-zh_en | 中英文 | TTS | Melo双语，1说话人 |
| kokoro-multi-lang-v1_0 | 中英文 | TTS | 多语言，53说话人 |

更多模型下载方法请参考 [模型下载指南](./MODELS.md)

## API文档

详细的API使用说明请参考 [API文档](./API.md)

## 注意事项

- 确保Python版本为3.10或更高
- 模型文件较大(总计约2GB)，请确保有足够存储空间
- 如遇到sherpa-onnx版本不兼容，可修改requirements.txt中的版本号
- 如端口8000被占用，使用`--port`参数指定其他端口
- 建议使用虚拟环境避免系统包管理冲突
