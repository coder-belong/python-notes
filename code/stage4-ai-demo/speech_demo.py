# speech_demo.py：语音转文字（ASR）：本机跑开源的 Whisper 小模型，再交给大模型整理成结构化的待办
import time
import wave

import numpy as np
from faster_whisper import WhisperModel

from llm import MODEL, NO_THINKING, client

# Whisper 是 OpenAI 开源的语音识别模型；faster-whisper 是跑得更快的版本，CPU 就行
# small：约 460MB，第一次运行自动下载；中文识别比 tiny / base 准不少
asr = WhisperModel("small", device="cpu", compute_type="int8")

# 读 16kHz 单声道的 wav，转成 -1～1 的小数数组（直接传文件路径要靠 av 库解码，它的版本和 faster-whisper 对不上会报错）
with wave.open("images/voice.wav") as f:
    audio = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16).astype(np.float32) / 32768

start = time.perf_counter()
segments, info = asr.transcribe(audio, language="zh")   # 录音是用 macOS 的 say 命令生成的
text = "".join(s.text for s in segments)
print(f"识别（{time.perf_counter() - start:.1f}s）：{text}")

# 识别出来的文字再交给大模型：和 4.4 节一样输出 JSON
resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": '把用户的话整理成 json：{"action": "做什么", "from": "原时间", "to": "新时间", "notify": "要通知谁、带什么"}'},
        {"role": "user", "content": text},
    ],
    response_format={"type": "json_object"},
    extra_body=NO_THINKING,
)
print(resp.choices[0].message.content)
