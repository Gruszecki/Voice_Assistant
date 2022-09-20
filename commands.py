import datetime
import easyocr
import mss
import numpy as np
import pynput
import subprocess

from configparser import ConfigParser
from PIL import Image, ImageDraw

from communication import speak, get_audio


commands_list = {
    'say_time()': [
        'która godzina',
        'jaki mamy czas',
        'która jest',
        'jaki jest czas'
    ],
    'open_app(text)': [
        'otwórz aplikację',
        'otwórz program',
        'włącz aplikację',
        'włącz program',
        'uruchom aplikację',
        'uruchom program',
    ],
    'press_key(text)': [
        'wciśnij klawisz',
        'naciśnij klawisz',
        'wciśnij przycisk',
        'naciśnij przycisk'
    ],
    'click_on_screen(text)': [
        'kliknij'
    ],
    'type(text)': [
        'pisz'      # Must be one command only
    ]
}
WAKE = 'janko'


config = ConfigParser()
config.read('config.ini')

keyboard_controller = pynput.keyboard.Controller()
mouse_controller = pynput.mouse.Controller()


def greetings():
    # speak(f'Nazywam się Janka. Jestem asystentem głosowym. Jeśli będziesz mnie potrzebował, zawołaj mnie: {WAKE}')
    speak(f'Zawołaj mnie: {WAKE}')

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
                command_to_type = ''
                if commands_list['type(text)'][0] in text:
                    index_to_type = text.index(commands_list['type(text)'][0])
                    command_to_type = text[index_to_type:]
                    text = text[:index_to_type]

                commands_split = text.split(' i ')
                commands = [command for command in commands_split if len(command)]

                if len(command_to_type):
                    commands.append(command_to_type)

                for command in commands:
                    result = execute_command(command)

                    if not result:
                        speak(f'Nie znalazłam akcji dla: {command}')

    return 1

def execute_command(text):
    for key, value in commands_list.items():
        for v in value:
            if v in text:
                exec(f'{key}')
                return 1

    return 0

def get_target_object(text: str, split_counter: int, ask_text: str):
    target_object = ' '.join(text.split()[split_counter:])

    # Check whether object is already provided or ask for it
    if target_object == '':
        speak(ask_text)
        target_object = validate_text(get_audio())

        if not target_object:
            return 0

    return target_object

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

def open_app(initial_text: str):
    target_object = get_target_object(initial_text, 2, 'Jaką aplikację mam otworzyć?')

    if target_object:
        try:
            app_path = config['apps'][target_object]
            subprocess.Popen(app_path)
        except KeyError:
            speak(f'Nie odnaleziono adresu aplikacji {target_object} w pliku konfiguracyjnym.')

def press_key(initial_text: str):
    target_object = get_target_object(initial_text, 2, 'Jaki klawisz mam wcisnąć?')

    if target_object:
        if len(target_object) == 1 and target_object.isalnum():
            try:
                keyboard_controller.press(target_object)
                keyboard_controller.release(target_object)
            except AttributeError:
                speak(f'Nie mogę wcisnąć klawisza {target_object}')
        else:
            match target_object:
                case 'start':
                    target_object = 'cmd'
                case 'escape':
                    target_object = 'esc'
                case 'tabulator':
                    target_object = 'tab'

            try:
                exec(f'keyboard_controller.press(pynput.keyboard.Key.{target_object})')
                exec(f'keyboard_controller.release(pynput.keyboard.Key.{target_object})')
            except AttributeError:
                speak(f'Nie mogę wcisnąć klawisza {target_object}')

def click_on_screen(initial_text: str):
    target_object = get_target_object(initial_text, 1, 'Co mam kliknąć?')

    if target_object:
        speak(f'Szukam {target_object}')
        with mss.mss() as sct:
            screenshot = sct.shot(mon=1, output='last_screenshot.png')

            reader = easyocr.Reader(['pl', 'en'])
            detected = reader.detect(screenshot, width_ths=0.7, mag_ratio=1.5)
            text_coordinates = detected[0][0]
            recognized = reader.recognize(screenshot, horizontal_list=text_coordinates, free_list=[])
            border_coordinates = [[txt[0][0], txt[0][2]] for txt in recognized if txt[1].lower() == target_object]

            if len(border_coordinates):
                target_x = int((border_coordinates[0][0][0] + border_coordinates[0][1][0]) / 2)
                target_y = int((border_coordinates[0][0][1] + border_coordinates[0][1][1]) / 2)

                mouse_controller.position = (target_x, target_y)
                mouse_controller.click(pynput.mouse.Button.left, count=1)

                speak('Wuala.')
            else:
                speak(f'Nie znalazłam {target_object}')

def make_transcription(text: str):
    capital = True
    result_text = ''
    for word in text.split():
        match word:
            case 'kropka':
                result_text += '\b. '
                capital = True
            case 'przecinek':
                result_text += '\b, '
            case 'pytajnik':
                result_text += '\b? '
            case 'dwukropek':
                result_text += '\b: '
            case 'średnik':
                result_text += '\b; '
            case 'myślnik':
                result_text += '- '
            case 'ukośnik' | 'slash':
                result_text += '\b/'
            case 'nawias':
                if result_text.count('(') > result_text.count(')'):
                    result_text += '\b) '
                else:
                    result_text += '('
            case 'cudzysłów':
                if result_text.count('"')/2:
                    result_text += '\b" '
                else:
                    result_text += '"'
            case 'enter':
                result_text += '\n'
            case 'xd':
                result_text += 'xD '
            case _:
                if not capital:
                    result_text += f'{word} '
                else:
                    result_text += f'{word.capitalize()} '
                    capital = False

    return result_text

def type(initial_text: str):
    key_word_place = initial_text.split().index(*commands_list['type(text)']) + 1
    target_object = get_target_object(initial_text, key_word_place, 'Co mam wpisać?')

    if target_object:
        target_text = make_transcription(target_object)
        keyboard_controller.type(target_text)

