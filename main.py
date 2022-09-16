import os
import pyttsx3
import speech_recognition as sr
import subprocess
import time


WAKE = 'janko'


def speak(text: str):
    engine = pyttsx3.init()
    engine.setProperty('rate', 175)
    engine.say(text)
    engine.runAndWait()


def get_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
        said = ''

        try:
            said = recognizer.recognize_google(audio, language='pl-PL')
            print(said)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio.")
            said = 'Nie zrozumiałam.'
        except sr.RequestError as e:
            print('Could not request results from Google Speech Recognition service:', str(e))
            said = 'Wystąpił błąd. Nie wiem co się dzieje.'

    return said.lower()


speak(f'Nazywam się Yanka. Jestem asystentem głosowym. Jeśli będziesz mnie potrzebował, zawołaj mnie tymi słowami: {WAKE}')

while True:
    text = get_audio()

    if text.count(WAKE) > 0:
        speak('Tak?')
        text = get_audio()

        if 'wyłącz się' in text:
            speak('Żegnam ozięble.')
            break
