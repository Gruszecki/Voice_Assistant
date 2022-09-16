import datetime
import subprocess
from configparser import ConfigParser

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
        'otwórz aplikację'
    ]
}

config = ConfigParser()
config.read('config.ini')


def greetings():
    speak(f'Nazywam się Yanka. Jestem asystentem głosowym. Jeśli będziesz mnie potrzebował, zawołaj mnie: {WAKE}')
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