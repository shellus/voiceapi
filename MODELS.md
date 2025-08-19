# 模型下载指南

所有模型文件存储在 `models` 目录中。根据需要下载相应的模型。

## 必需模型

### silero_vad.onnx
> ASR功能必需的VAD(语音活动检测)模型

```bash
mkdir -p silero_vad
cd silero_vad
curl -SL -o silero_vad.onnx https://github.com/snakers4/silero-vad/raw/master/src/silero_vad/data/silero_vad.onnx
cd ..
```

## ASR模型

### sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20 (推荐)
**中英双语流式识别模型**
```bash
curl -SL -O https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20.tar.bz2
tar -xjf sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20.tar.bz2
```

### FireRedASR-AED-L
**高精度中英双语模型**
```bash
curl -SL -O https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-fire-red-asr-large-zh_en-2025-02-16.tar.bz2
tar -xjf sherpa-onnx-fire-red-asr-large-zh_en-2025-02-16.tar.bz2
```

### sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17
**多语言离线识别模型(中英日韩粤)**
```bash
curl -SL -O https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17.tar.bz2
tar -xjf sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17.tar.bz2
```

### sherpa-onnx-paraformer-trilingual-zh-cantonese-en
**中文+粤语+英文三语模型**
```bash
curl -SL -O https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-paraformer-trilingual-zh-cantonese-en.tar.bz2
tar -xjf sherpa-onnx-paraformer-trilingual-zh-cantonese-en.tar.bz2
```

### sherpa-onnx-paraformer-en-2024-03-09
**英文专用模型**
```bash
curl -SL -O https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-paraformer-en-2024-03-09.tar.bz2
tar -xjf sherpa-onnx-paraformer-en-2024-03-09.tar.bz2
```

### sherpa-onnx-streaming-paraformer-bilingual-zh-en
**中英双语流式模型**
```bash
curl -SL -O https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-streaming-paraformer-bilingual-zh-en.tar.bz2
tar -xjf sherpa-onnx-streaming-paraformer-bilingual-zh-en.tar.bz2
```

### sherpa-onnx-whisper-tiny.en
**轻量级英文模型**
```bash
curl -SL -O https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-tiny.en.tar.bz2
tar -xjf sherpa-onnx-whisper-tiny.en.tar.bz2
```

## TTS模型

### vits-zh-hf-theresa (推荐)
**中文语音合成，804个说话人**
```bash
curl -SL -O https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-zh-hf-theresa.tar.bz2
tar -xjf vits-zh-hf-theresa.tar.bz2
```

### vits-melo-tts-zh_en
**中英双语语音合成**
```bash
curl -SL -O https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-melo-tts-zh_en.tar.bz2
tar -xjf vits-melo-tts-zh_en.tar.bz2
```

### kokoro-multi-lang-v1_0
**多语言语音合成，53个说话人**
```bash
curl -SL -O https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-multi-lang-v1_0.tar.bz2
tar -xjf kokoro-multi-lang-v1_0.tar.bz2
```

## 网络问题解决方案

如果遇到GitHub访问问题，可以使用以下方法：

### 方法1: 使用代理
```bash
~/proxy-env.sh curl -SL -O [模型下载链接]
```

### 方法2: 使用GitHub镜像
```bash
# 将github.com替换为gh.llkk.cc
curl -SL -O https://gh.llkk.cc/k2-fsa/sherpa-onnx/releases/download/asr-models/[模型文件名]
```

## 模型选择建议

### ASR模型选择
- **实时流式识别**: `sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20`
- **高精度离线识别**: `sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17`
- **多语言支持**: `sherpa-onnx-paraformer-trilingual-zh-cantonese-en`
- **英文专用**: `sherpa-onnx-paraformer-en-2024-03-09`

### TTS模型选择
- **中文语音**: `vits-zh-hf-theresa` (多说话人选择)
- **中英双语**: `vits-melo-tts-zh_en`
- **多语言**: `kokoro-multi-lang-v1_0`

## 存储空间要求

- ASR模型: 通常100MB-1GB
- TTS模型: 通常50MB-500MB
- 建议预留至少2GB空间用于模型存储

## 模型更新

定期检查 [sherpa-onnx releases](https://github.com/k2-fsa/sherpa-onnx/releases) 获取最新模型版本。
