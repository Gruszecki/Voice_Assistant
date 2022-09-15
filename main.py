import os
import pyttsx3
import speech_recognition as sr
import time


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
        except sr.RequestError as e:
            print('Could not request results from Google Speech Recognition service:', str(e))

    return said


speak('Nazywam się Felicjankobot. Jak mogę ci pomóc?')