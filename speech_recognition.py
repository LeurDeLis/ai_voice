# import pyttsx3
#
# engine = pyttsx3.init()
# engine.say("你好，潘晶晶！")
# engine.runAndWait()


import sounddevice as sd
from vosk import Model, KaldiRecognizer
import queue
import signal
import sys
import json

# 初始化 Vosk 模型
model = Model("vosk-model-cn-0.22")
rec = KaldiRecognizer(model, 16000)

# 创建队列用于音频传输
q = queue.Queue()

# 音频回调函数，将数据推入队列
def callback(indata, frames, time, status):
    if status:
        print(f"音频状态: {status}", file=sys.stderr)
    q.put(bytes(indata))

# 信号处理：按 Ctrl+C 优雅退出
def signal_handler(sig, frame):
    print("\n识别终止，程序已退出。")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# 主识别函数
def recognize_forever():
    print("🎤 语音识别已启动，请开始说话（按 Ctrl+C 退出）...\n")
    with sd.InputStream(samplerate=16000, channels=1, dtype='int16', callback=callback):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text.strip():
                    print("🗣️ 识别结果：", text.replace(" ", ""))
            else:
                partial = json.loads(rec.PartialResult())
                if partial.get("partial"):
                    print("（临时）", partial["partial"], end='\r')

# 启动识别
recognize_forever()



