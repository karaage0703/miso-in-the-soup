import ollama
import pygame
import sys
import time
import textwrap
import threading
import math
import random
import cv2
import numpy as np

from system_prompt import base_prompt

from pathlib import Path
import voicevox_core
from voicevox_core import AccelerationMode, AudioQuery, VoicevoxCore
from playsound import playsound

SPEAKER_ID = 2

open_jtalk_dict_dir = './open_jtalk_dic_utf_8-1.11'
# text = 'これはテストです'
out = Path('output.wav')
acceleration_mode = AccelerationMode.AUTO


WINDOW_WIDTH = 640
WINDOW_HEIGHT = 640

WAIT_TIME_WORD = 2
WAIT_TIME_IMAGE = 0.01

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


def draw_text_with_outline(screen, text, font, text_color, outline_color, max_width, window_width, window_height):
    """指定されたテキストを縁取り付きで描画します。

    Args:
        screen (pygame.Surface): テキストを描画するスクリーン。
        text (str): 描画するテキスト。
        font (pygame.font.Font): 使用するフォント。
        text_color (tuple): テキストの色（RGB）。
        outline_color (tuple): 縁取りの色（RGB）。
        max_width (int): テキストを改行する最大幅。
        window_width (int): ウィンドウの幅。
        window_height (int): ウィンドウの高さ。
    """
    # テキストを改行して分割
    wrapped_text = textwrap.wrap(text, width=max_width)

    # 各行の高さを取得
    line_height = font.get_linesize()

    # 各行を描画
    for i, line in enumerate(wrapped_text):
        outline_width = 2

        # テキストをレンダリングして、そのサイズを取得
        main_text = font.render(line, True, text_color)
        text_rect = main_text.get_rect(center=(window_width / 2, window_height / 2 + i * line_height - (len(wrapped_text) * line_height) / 2))

        # 縁取りのテキストを描画
        outline_positions = [
            (text_rect.x - outline_width, text_rect.y - outline_width),
            (text_rect.x + outline_width, text_rect.y - outline_width),
            (text_rect.x - outline_width, text_rect.y + outline_width),
            (text_rect.x + outline_width, text_rect.y + outline_width),
        ]
        for outline_pos in outline_positions:
            outline_text = font.render(line, True, outline_color)
            outline_rect = outline_text.get_rect(topleft=outline_pos)
            screen.blit(outline_text, outline_rect)

        # 本体のテキストを描画
        screen.blit(main_text, text_rect)


def draw_video_frame(screen, cap, window_width, window_height):
    """
    スクリーンに動画のフレームを描画します。

    Args:
        screen (pygame.Surface): 動画のフレームを描画するスクリーン。
        cap (cv2.VideoCapture): 動画キャプチャオブジェクト。
        window_width (int): ウィンドウの幅。
        window_height (int): ウィンドウの高さ。
    """

    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = cap.read()

    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)  # フレームを反時計回りに90度回転
    frame = cv2.resize(frame, (window_width, window_height))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_surface = pygame.surfarray.make_surface(frame)
    screen.blit(frame_surface, (0, 0))


def draw_image(screen, image, window_width, window_height, frame_count):
    """
    スクリーンに画像を描画し、スケーリング、明るさ、コントラストの調整を行います。

    Args:
        screen (pygame.Surface): 画像を描画するためのサーフェス。
        image (pygame.Surface): 描画する画像。
        window_width (int): ウィンドウの幅。
        window_height (int): ウィンドウの高さ。
        frame_count (int): トランスフォーメーションを決定する現在のフレーム数。
    """

    # サイン波とランダム変動を使用してスケールファクターを計算
    scale_factor = 0.8 + 0.05 * math.sin(frame_count * 0.1) + 0.002 * random.uniform(-1, 1)
    scaled_width = int(window_width * scale_factor)
    scaled_height = int(window_height * scale_factor)

    # 画像のリサイズ
    resized_image = pygame.transform.scale(image, (scaled_width, scaled_height))

    # 透過処理のために新しいサーフェスを作成
    resized_image = resized_image.convert_alpha()
    width, height = resized_image.get_size()
    for x in range(width):
        for y in range(height):
            r, g, b, a = resized_image.get_at((x, y))
            if r == 0 and g == 0 and b == 0:
                resized_image.set_at((x, y), (r, g, b, 0))

    # リサイズされた画像の矩形を取得し、スクリーンの中央に配置
    image_rect = resized_image.get_rect(center=(window_width / 2, window_height / 2))

    # 画像をスクリーンに描画
    screen.blit(resized_image, image_rect)


def main():
    global message
    frame_count = 0

    # Pygameを初期化
    pygame.init()

    # 画面サイズを設定
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption('miso in the soup')

    # 背景動画の読み込み
    cap = cv2.VideoCapture('./images/background_miso.mp4')
    if not cap.isOpened():
        print("Error: Could not open video file.")
        return

    # フォントとサイズを設定
    font = pygame.font.Font('./fonts/NotoSansJP-Regular.ttf', 70)

    # 表示するテキストを設定
    text_color = (255, 255, 255)
    outline_color = (0, 0, 0)

    # PNG画像をロード
    image = pygame.image.load('./images/miso.png').convert_alpha()

    # メッセージ取得スレッドを開始
    message_thread = threading.Thread(target=get_message)
    message_thread.daemon = True
    message_thread.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                window_width, window_height = event.w, event.h

        # 現在のウィンドウサイズを取得
        window_width, window_height = screen.get_size()

        # 動画のフレームを描画
        draw_video_frame(screen, cap, window_width, window_height)

        # 画像を描画
        draw_image(screen, image, window_width, window_height, frame_count)

        # テキストを縁取り付きで描画
        draw_text_with_outline(screen, message, font, text_color, outline_color, max_width=5, window_width=window_width, window_height=window_height)

        # 画面を左右反転
        # flipped_screen = pygame.transform.flip(screen, True, False)

        # 反転された画面を描画
        # screen.blit(flipped_screen, (0, 0))

        # 画面を更新
        pygame.display.flip()

        frame_count += 1
        time.sleep(WAIT_TIME_IMAGE)


if __name__ == '__main__':
    main()
