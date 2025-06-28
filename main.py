import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import os
import signal
import sys
import json
import pyttsx3
import pyaudio
from PyQt5 import QtWidgets, QtCore, QtGui
from dashscope.audio.asr import *
import dashscope
from openai import OpenAI
from ai_voice import Ui_MainWindow
from speak import *

sample_rate = 16000
block_size = 3200
format_pcm = 'pcm'
init_dashscope_api_key()

class Callback(RecognitionCallback):
    def __init__(self, ui_callback):
        super().__init__()
        self.stream = None
        self.mic = None
        self.ui_callback = ui_callback

    def on_open(self):
        self.mic = pyaudio.PyAudio()
        self.stream = self.mic.open(format=pyaudio.paInt16,
                                    channels=1,
                                    rate=sample_rate,
                                    input=True)
        self.ui_callback.set_stream(self.stream)

    def on_close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.mic.terminate()
        self.ui_callback.clear_stream()
        self.ui_callback._can_send_audio = False  # 设置标志位防止继续发送

    def on_event(self, result: RecognitionResult):
        sentence = result.get_sentence()
        if 'text' in sentence:
            text = sentence['text']
            print('RecognitionCallback text:', text)
            if RecognitionResult.is_sentence_end(sentence):
                print('RecognitionCallback sentence end')
                self.ui_callback.handle_result(text)

    def on_error(self, message):
        print('Error:', message.message)
        sys.exit(1)


def init_dashscope_api_key():
    if 'DASHSCOPE_API_KEY' in os.environ:
        dashscope.api_key = os.environ['DASHSCOPE_API_KEY']
    else:
        dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")


def speak(text):
    synthesis_text_to_speech_and_play_by_streaming_mode(
        text=text)
    # self.engine.say(text)
    # self.engine.runAndWait()


class VoiceAssistantWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.stream = None
        self.is_open_chat = False
        self._can_send_audio = True  # 新增标志位控制是否允许发送音频帧

        self.client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

        init_dashscope_api_key()

        self.callback = Callback(self)
        self.recognition = Recognition(
            model='paraformer-realtime-v2',
            format=format_pcm,
            sample_rate=sample_rate,
            semantic_punctuation_enabled=False,
            callback=self.callback
        )

        self.recognition.start()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.read_audio_frame)
        self.timer.start(100)

        signal.signal(signal.SIGINT, self.exit_app)

    def set_stream(self, stream):
        self.stream = stream

    def clear_stream(self):
        self.stream = None

    def read_audio_frame(self):
        if self.stream:
            try:
                data = self.stream.read(block_size, exception_on_overflow=False)
                # 检查 recognition 是否可用
                if getattr(self, '_can_send_audio', True):
                    self.recognition.send_audio_frame(data)
            except Exception as e:
                print("⚠️ 发送音频帧失败:", str(e))
                self._can_send_audio = False  # 标记不可再发送音频帧

    def handle_result(self, text):
        text = text.strip()
        reply = ""

        if not text:
            return

        self.textEdit.append(f"🗣️ 你说：{text}")

        if "退出" in text:
            reply ="好的，再见！"
            self.exit_app()
        elif "退下" in text:
            reply = "好的，有需要再叫我！"
            self.is_open_chat = False
        elif "小爱同学" in text:
            reply = "我在！"
            self.is_open_chat = True
        elif self.is_open_chat:
            reply = self.get_llm_response(text)

        if reply:
            self.textEdit.append(f"🤖 回复：{reply}")
            self.textEdit.moveCursor(QtGui.QTextCursor.End)
            speak(reply)
            reply = ""


    def get_llm_response(self, prompt):
        try:
            completion = self.client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {"role": "system", "content": "请谨记你的名字是\"小爱同学\", 不管谁问你你都是小爱同学！你是一个有用的语音助手。可以帮助我解答日常遇到的生活问题，处理工作中遇到的难题，还可以提供旅行攻略、烹饪方案的帮助。"},
                    {"role": "user", "content": prompt},
                ]
            )
            res = json.loads(completion.model_dump_json())
            return res["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"❌ [错误] 大模型回复失败: {e}")
            return None

    def exit_app(self, *args):
        print("🛑 正在退出程序...")
        self._can_send_audio = False  # 提前阻止继续发送
        try:
            self.recognition.stop()
        except Exception as e:
            print(f"❌ [错误] 语音识别停止失败: {e}")
            signal.signal(signal.SIGINT, signal.SIG_DFL)
        sys.exit(0)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = VoiceAssistantWindow()
    window.show()
    sys.exit(app.exec_())
