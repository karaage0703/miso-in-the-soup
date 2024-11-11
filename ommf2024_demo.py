from pathlib import Path

import ollama
from playsound import playsound
from voicevox_core import AccelerationMode, VoicevoxCore

from system_prompt import base_prompt

import miso_in_the_soup_xiao as xiao

SPEAKER_ID = 2

ACCELERATION_MODE = AccelerationMode.AUTO
OPEN_JTALK_DICT_DIR = "./open_jtalk_dic_utf_8-1.11"
WAVE_FILE = Path("output.wav")

XIAO_SERIAL_NAME = "/dev/ttyACM0"


def get_stream_message():
    response = ollama.chat(
        # model='gemma:2b',
        model="7shi/tanuki-dpo-v1.0:8b-q6_K",
        messages=[{"role": "user", "content": base_prompt}],
        stream=True,
    )

    chunks = []
    for chunk in response:
        content = chunk["message"]["content"]
        print(content, end="", flush=True)
        chunks.append(content)

    full_message = "".join(chunks)

    return full_message


def main():
    xiao.open(XIAO_SERIAL_NAME)
    xiao.setLed(0)

    core = VoicevoxCore(
        acceleration_mode=ACCELERATION_MODE, open_jtalk_dict_dir=OPEN_JTALK_DICT_DIR
    )
    core.load_model(SPEAKER_ID)

    while True:
        # 考え中
        xiao.setLed(2)
        full_message = get_stream_message()
        print("")

        # 改行とタブ文字を取り除く
        full_message = (
            full_message.replace("\n", "")
            .replace("\r", "")
            .replace("\t", "")
            .replace("「", "")
            .replace("」", "")
            .replace("</llm-code-output>", "")
        )

        # 音声生成
        audio_query = core.audio_query(full_message, SPEAKER_ID)
        wav = core.synthesis(audio_query, SPEAKER_ID)
        WAVE_FILE.write_bytes(wav)

        # 音声出力
        xiao.setLed(1)
        playsound(WAVE_FILE)


if __name__ == "__main__":
    main()
