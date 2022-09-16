import subprocess
import datetime

import communication

WAKE = 'janko'

commands_list = {
    'say_time': [
        'która godzina',
        'jaki mamy czas',
        'która jest',
        'jaki jest czas'
    ]
}


def greetings():
    # communication.speak(f'Nazywam się Yanka. Jestem asystentem głosowym. Jeśli będziesz mnie potrzebował, zawołaj mnie: {WAKE}')
    communication.speak(f'Zawołaj mnie: {WAKE}')

def validate_text(text):
    match text:
        case 'NOT UNDERSTOOD':
            communication.speak('Nie zrozumiałam.')
            return 0
        case 'ERROR':
            communication.speak('Wystąpił błąd. Nie wiem co się dzieje.')
            return 0
        case _:
            return text

def listen():
    text = communication.get_audio()
    print(text)
    if text.count(WAKE) > 0:
        communication.speak('Tak?')
        text = validate_text(communication.get_audio())

        if text:
            if 'wyłącz się' in text:
                communication.speak('Żegnam ozięble.')
                return 0
            else:
                result = execute_command(text)

                if not result:
                    communication.speak(f'Nie znalazłam akcji dla: {text}')

    return 1

def execute_command(text):
    print('Szukam', text)
    for key, value in commands_list.items():
        print(key, value)
        if text in value:
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
            text += f'{time_now[1]} minut po północy'
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

    if hour:
        text += minutes

    communication.speak(text)
