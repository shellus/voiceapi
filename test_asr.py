#!/usr/bin/env python3
"""
ASR功能测试脚本
使用test_audio文件夹中的PCM音频文件测试ASR WebSocket功能
"""

import asyncio
import websockets
import json
import os
import time
from pathlib import Path

class ASRTester:
    def __init__(self, server_url="ws://localhost:8003"):
        self.server_url = server_url
        self.test_audio_dir = Path("test_audio")
        
    async def test_asr_with_file(self, pcm_file, chunk_size=1024):
        """使用PCM文件测试ASR功能"""
        print(f"\n🎵 测试文件: {pcm_file}")
        print(f"📁 文件大小: {os.path.getsize(pcm_file)} bytes")
        
        # 连接WebSocket
        uri = f"{self.server_url}/asr?samplerate=16000"
        print(f"🔗 连接到: {uri}")
        
        try:
            async with websockets.connect(uri, timeout=60) as websocket:
                print("✅ WebSocket连接成功")

                # ASR引擎已预加载，直接发送音频数据
                
                # 读取PCM文件并分块发送
                with open(pcm_file, 'rb') as f:
                    chunk_count = 0
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        
                        await websocket.send(chunk)
                        chunk_count += 1
                        
                        # 模拟实时音频流，添加小延迟
                        await asyncio.sleep(0.032)  # 32ms延迟，模拟16kHz采样率
                        
                        if chunk_count % 10 == 0:
                            print(f"📤 已发送 {chunk_count} 个音频块")
                
                print(f"📤 音频发送完成，共发送 {chunk_count} 个块")
                
                # 收集识别结果
                results = []
                timeout_count = 0
                max_timeout = 10  # 最多等待10次超时
                
                while timeout_count < max_timeout:
                    try:
                        # 等待识别结果，设置超时
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(message)
                        
                        print(f"📥 收到结果: {data}")
                        results.append(data)
                        
                        # 如果收到finished=True的结果，说明识别完成
                        if data.get('finished', False):
                            print("🎯 识别完成")
                            break
                            
                        timeout_count = 0  # 重置超时计数
                        
                    except asyncio.TimeoutError:
                        timeout_count += 1
                        print(f"⏰ 等待结果超时 ({timeout_count}/{max_timeout})")
                        
                        if timeout_count >= max_timeout:
                            print("⚠️ 等待超时，结束测试")
                            break
                
                return results
                
        except Exception as e:
            print(f"❌ 连接错误: {e}")
            return None
    
    def analyze_results(self, results, test_name):
        """分析识别结果"""
        print(f"\n📊 {test_name} 测试结果分析:")
        print("=" * 50)
        
        if not results:
            print("❌ 没有收到任何识别结果")
            return
        
        # 提取所有文本
        all_texts = []
        finished_texts = []
        
        for result in results:
            text = result.get('text', '')
            finished = result.get('finished', False)
            idx = result.get('idx', 0)
            
            if text:
                all_texts.append(text)
                if finished:
                    finished_texts.append(text)
                    print(f"✅ 完成片段 {idx}: {text}")
                else:
                    print(f"🔄 进行中 {idx}: {text}")
        
        print(f"\n📝 最终识别结果:")
        if finished_texts:
            final_text = " ".join(finished_texts)
            print(f"🎯 完整文本: {final_text}")
        else:
            print("⚠️ 没有完成的识别结果")
        
        print(f"📊 统计信息:")
        print(f"   - 总消息数: {len(results)}")
        print(f"   - 完成片段数: {len(finished_texts)}")
        print(f"   - 进行中片段数: {len(all_texts) - len(finished_texts)}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始ASR功能测试")
        print("=" * 60)
        
        # 检查测试音频目录
        if not self.test_audio_dir.exists():
            print(f"❌ 测试音频目录不存在: {self.test_audio_dir}")
            return
        
        # 测试用例定义
        test_cases = [
            ("1.pcm", "VAD检测和ASR断句测试"),
            ("2.pcm", "静默断句测试"),
            ("3.pcm", "别打断正常停顿测试"),
            ("4.pcm", "别打断拖音停顿测试"),
        ]
        
        for pcm_file, test_name in test_cases:
            pcm_path = self.test_audio_dir / pcm_file
            
            if not pcm_path.exists():
                print(f"⚠️ 跳过测试: {pcm_file} (文件不存在)")
                continue
            
            print(f"\n{'='*20} {test_name} {'='*20}")
            
            # 执行测试
            results = await self.test_asr_with_file(pcm_path)
            
            # 分析结果
            if results:
                self.analyze_results(results, test_name)
            else:
                print(f"❌ {test_name} 测试失败")
            
            # 测试间隔
            print("\n⏳ 等待3秒后进行下一个测试...")
            await asyncio.sleep(3)
        
        print("\n🎉 所有测试完成!")

async def main():
    """主函数"""
    print("ASR WebSocket 测试工具")
    print("=" * 40)
    
    # 检查服务器是否运行
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8003/') as resp:
                if resp.status == 200:
                    print("✅ 服务器运行正常")
                else:
                    print(f"⚠️ 服务器响应异常: {resp.status}")
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("请确保服务器在 http://localhost:8003 运行")
        return
    
    # 创建测试器并运行测试
    tester = ASRTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    # 安装依赖提示
    try:
        import websockets
        import aiohttp
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("请安装依赖: pip install websockets aiohttp")
        exit(1)
    
    # 运行测试
    asyncio.run(main())
