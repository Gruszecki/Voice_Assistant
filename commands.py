import datetime
import easyocr
import mss
import numpy as np
import pynput
import subprocess

from configparser import ConfigParser
from PIL import Image, ImageDraw

from communication import speak, get_audio


WAKE = 'janko'

commands_list = {
    'say_time': [
        'która godzina',
        'jaki mamy czas',
        'która jest',
        'jaki jest czas'
    ],
    'open_app': [
        'otwórz aplikację',
        'otwórz program',
        'włącz aplikację',
        'włącz program'
    ],
    'press_key': [
        'wciśnij klawisz'
    ],
    'click_on_screen': [
        'kliknij'
    ]
}

config = ConfigParser()
config.read('config.ini')

keyboard = pynput.keyboard.Controller()
mouse = pynput.mouse.Controller()


def greetings():
    speak(f'Nazywam się Janka. Jestem asystentem głosowym. Jeśli będziesz mnie potrzebował, zawołaj mnie: {WAKE}')
    # speak(f'Zawołaj mnie: {WAKE}')

def validate_text(text):
    match text:
        case 'NOT UNDERSTOOD':
            speak('Nie zrozumiałam.')
            return 0
        case 'ERROR':
            speak('Wystąpił błąd. Nie wiem co się dzieje.')
            return 0
        case _:
            return text

def listen():
    text = get_audio()

    if text.count(WAKE) > 0:
        speak('Tak?')
        text = validate_text(get_audio())

        if text:
            if 'wyłącz się' in text:
                speak('Żegnam ozięble.')
                return 0
            else:
                result = execute_command(text)

                if not result:
                    speak(f'Nie znalazłam akcji dla: {text}')

    return 1

def execute_command(text):
    for key, value in commands_list.items():
        for v in value:
            if v in text:
                exec(f'{key}()')
                return 1

    return 0


def say_time():
    time_now = str(datetime.datetime.now().time()).split(':')
    hour = int(time_now[0])
    minutes = time_now[1]
    text = ''

    match hour:
        case 0:
            text += 'zero '
        case 4 | 5 | 6 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20:
            text += f'{hour}-ta '
        case 1 | 21:
            text += f'{hour}-sza '
        case 2 | 22:
            text += f'{hour}-ga '
        case 3 | 23:
            text += f'{hour}-cia '
        case 7 | 8:
            text += f'{hour}-ma '

    text += minutes

    speak(text)

def open_app():
    speak('Jaką aplikację mam otworzyć?')
    text = validate_text(get_audio())

    if text:
        try:
            app_path = config['apps'][text]
            subprocess.Popen(app_path)
        except KeyError:
            speak(f'Nie odnaleziono adresu aplikacji {text} w pliku konfiguracyjnym.')

def press_key():
    speak('Jaki klawisz mam wcisnąć?')
    text = validate_text(get_audio())

    if text:
        if len(text) == 1 and text.isalnum():
            try:
                keyboard.press(text)
                keyboard.release(text)
            except AttributeError:
                speak(f'Nie mogę wcisnąć klawisza {text}')
        else:
            match text:
                case 'start':
                    text = 'cmd'

            try:
                exec(f'keyboard.press(pynput.keyboard.Key.{text})')
                exec(f'keyboard.release(pynput.keyboard.Key.{text})')
            except AttributeError:
                speak(f'Nie mogę wcisnąć klawisza {text}')

def click_on_screen():
    speak('Co mam kliknąć?')
    voice_text = validate_text(get_audio())

    if voice_text:
        speak(f'Szukam {voice_text}')
        with mss.mss() as sct:
            screenshot = sct.shot(mon=1, output='last_screenshot.png')

            reader = easyocr.Reader(['pl', 'en'])
            detected = reader.detect(screenshot, width_ths=0.7, mag_ratio=1.5)
            text_coordinates = detected[0][0]
            recognized = reader.recognize(screenshot, horizontal_list=text_coordinates, free_list=[])
            border_coordinates = [[txt[0][0], txt[0][2]] for txt in recognized if txt[1].lower() == voice_text]

            if len(border_coordinates):
                target_x = int((border_coordinates[0][0][0] + border_coordinates[0][1][0]) / 2)
                target_y = int((border_coordinates[0][0][1] + border_coordinates[0][1][1]) / 2)

                mouse.position = (target_x, target_y)
                mouse.click(pynput.mouse.Button.left, count=1)
            else:
                speak(f'Nie znalazłam {voice_text}')
