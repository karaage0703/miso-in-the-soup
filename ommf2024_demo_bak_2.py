import ollama
import sys
import time
import threading
import random
import cv2
import numpy as np

from system_prompt import base_prompt

from pathlib import Path
import voicevox_core
from voicevox_core import AccelerationMode, AudioQuery, VoicevoxCore
from playsound import playsound
import warnings
warnings.filterwarnings('ignore')

SPEAKER_ID = 2

open_jtalk_dict_dir = './open_jtalk_dic_utf_8-1.11'
out = Path('output.wav')
acceleration_mode = AccelerationMode.AUTO

WAIT_TIME_WORD = 2

message = ""


def get_message():
    global message
    while True:
        response = ollama.chat(
            # model='gemma:2b',
            model='7shi/tanuki-dpo-v1.0:8b-q6_K',            
            messages=[{'role': 'user', 'content': base_prompt}],
        )
        message_content = response['message']['content']

        # 改行とタブ文字を取り除く
        message = message_content.replace('\n', '').replace('\r', '').replace('\t', '')

        core = VoicevoxCore(
            acceleration_mode=acceleration_mode, open_jtalk_dict_dir=open_jtalk_dict_dir
        )
        core.load_model(SPEAKER_ID)
        audio_query = core.audio_query(message, SPEAKER_ID)
        wav = core.synthesis(audio_query, SPEAKER_ID)
        out.write_bytes(wav)
        playsound(out)

        time.sleep(WAIT_TIME_WORD)


def main():
    global message

    # メッセージ取得スレッドを開始
    message_thread = threading.Thread(target=get_message)
    message_thread.daemon = True
    message_thread.start()

    while True:
        print(message)

        time.sleep(1)


if __name__ == '__main__':
    main()
