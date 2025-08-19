# API 使用文档

## WebSocket 流式API

### /asr - 语音识别
通过WebSocket发送PCM 16bit音频数据到服务器，服务器返回转录结果。

**查询参数:**
- `samplerate`: 采样率，默认16000

**返回格式:**
服务器返回JSON格式的转录结果，包含以下字段：
- `text`: 转录结果文本
- `finished`: 该段是否完成
- `idx`: 段落索引

**JavaScript示例:**
```javascript
const ws = new WebSocket('ws://localhost:8000/asr?samplerate=16000');
ws.onopen = () => {
    console.log('connected');
    ws.send('{"sid": 0}');
};
ws.onmessage = (e) => {
    const data = JSON.parse(e.data);
    const { text, finished, idx } = data;
    // 处理转录文本
    // finished为true时表示该段完成
};
// 发送音频数据
// PCM 16bit格式，指定采样率
ws.send(int16Array.buffer);
```

### /tts - 语音合成
发送文本到服务器，服务器返回合成的音频数据。

**查询参数:**
- `samplerate`: 采样率，默认16000
- `sid`: 说话人ID，默认0
- `speed`: 语音速度，默认1.0
- `chunk_size`: 音频块大小，默认1024

**返回格式:**
- 音频数据：PCM 16bit格式的二进制数据
- 状态信息：JSON格式，包含以下字段：
  - `elapsed`: 耗时
  - `progress`: 合成进度
  - `duration`: 音频时长
  - `size`: 音频数据大小

**JavaScript示例:**
```javascript
const ws = new WebSocket('ws://localhost:8000/tts?samplerate=16000');
ws.onopen = () => {
    console.log('connected');
    ws.send('您要合成的文本内容');
};
ws.onmessage = (e) => {
    if (e.data instanceof Blob) {
        // 分块音频数据
        e.data.arrayBuffer().then((arrayBuffer) => {
            const int16Array = new Int16Array(arrayBuffer);
            let float32Array = new Float32Array(int16Array.length);
            for (let i = 0; i < int16Array.length; i++) {
                float32Array[i] = int16Array[i] / 32768.;
            }
            playNode.port.postMessage({ 
                message: 'audioData', 
                audioData: float32Array 
            });
        });
    } else {
        // 服务器返回合成状态信息
        const {elapsed, progress, duration, size } = JSON.parse(e.data);
        console.log(`耗时: ${elapsed}ms, 进度: ${progress}%`);
    }
};
```

## HTTP API

### POST /tts - 语音合成
发送文本到服务器，返回合成的音频文件。

**请求参数:**
- `text`: 要合成的文本
- `samplerate`: 采样率，默认16000
- `sid`: 说话人ID，默认0
- `speed`: 语音速度，默认1.0

**cURL示例:**
```bash
curl -X POST "http://localhost:8000/tts" \
     -H "Content-Type: application/json" \
     -d '{
           "text": "你好，世界！",
           "sid": 0,
           "samplerate": 16000,
           "speed": 1.0
         }' -o hello_world.wav
```

**Python示例:**
```python
import requests

url = "http://localhost:8000/tts"
data = {
    "text": "你好，世界！",
    "sid": 0,
    "samplerate": 16000,
    "speed": 1.0
}

response = requests.post(url, json=data)
with open("hello_world.wav", "wb") as f:
    f.write(response.content)
```

## 错误处理

所有API在出错时会返回相应的错误信息：

**WebSocket错误:**
```json
{
    "error": "错误描述",
    "code": "错误代码"
}
```

**HTTP错误:**
```json
{
    "detail": "错误详细信息"
}
```

## 性能优化建议

1. **音频格式**: 使用PCM 16bit格式可获得最佳性能
2. **采样率**: 推荐使用16000Hz，平衡质量和性能
3. **连接复用**: WebSocket连接可复用，避免频繁建立连接
4. **分块处理**: 对于长音频，建议分块发送和处理
