from pathlib import Path

import ollama
from playsound import playsound
from voicevox_core import AccelerationMode, VoicevoxCore

from system_prompt import base_prompt

SPEAKER_ID = 2

open_jtalk_dict_dir = "./open_jtalk_dic_utf_8-1.11"
out = Path("output.wav")
acceleration_mode = AccelerationMode.AUTO

WAIT_TIME_WORD = 2

message = ""


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
    core = VoicevoxCore(
        acceleration_mode=acceleration_mode, open_jtalk_dict_dir=open_jtalk_dict_dir
    )
    core.load_model(SPEAKER_ID)

    while True:
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

        # 音声出力
        audio_query = core.audio_query(full_message, SPEAKER_ID)
        wav = core.synthesis(audio_query, SPEAKER_ID)
        out.write_bytes(wav)
        playsound(out)


if __name__ == "__main__":
    main()
