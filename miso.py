import ollama
import pygame
import sys
import time
import textwrap

from system_prompt import base_prompt

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 640

WAIT_TIME = 3


def get_message():
    """Ollamaモデルを使用してチャットメッセージを送信し、応答メッセージを返します。

    Returns:
        clean_message (str): 応答メッセージの内容。
    """
    response = ollama.chat(
        model='gemma:2b',
        messages=[{'role': 'user', 'content': base_prompt}],
    )
    message = response['message']['content']

    # 改行とタブ文字を取り除く
    clean_message = message.replace('\n', '').replace('\r', '').replace('\t', '')

    return clean_message


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
        # 縁取りの幅
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


def main():
    # Pygameを初期化
    pygame.init()

    # 画面サイズを設定
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption('miso in the soup')

    # 背景色を黒に設定
    background_color = (0, 0, 0)

    # フォントとサイズを設定
    font = pygame.font.Font('./fonts/NotoSansJP-Regular.ttf', 70)

    # 表示するテキストを設定
    text_color = (255, 255, 255)
    outline_color = (0, 0, 0)

    # PNG画像をロード
    image = pygame.image.load('./images/miso.png')

    # メインループ
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                window_width, window_height = event.w, event.h

        # 現在のウィンドウサイズを取得
        window_width, window_height = screen.get_size()

        # 背景を塗りつぶす
        screen.fill(background_color)

        text = get_message()
        print(text)

        # 画像をリサイズして描画
        resized_image = pygame.transform.scale(image, (window_width, window_height))
        image_rect = resized_image.get_rect(center=(window_width / 2, window_height / 2))
        screen.blit(resized_image, image_rect)

        # テキストを縁取り付きで描画
        draw_text_with_outline(screen, text, font, text_color, outline_color, max_width=5, window_width=window_width, window_height=window_height)

        # 画面を左右反転
        flipped_screen = pygame.transform.flip(screen, True, False)

        # 反転された画面を描画
        screen.blit(flipped_screen, (0, 0))

        # 画面を更新
        pygame.display.flip()

        time.sleep(WAIT_TIME)


if __name__ == '__main__':
    main()
