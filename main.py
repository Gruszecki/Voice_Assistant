import os
import playsound
import speech_recognition as sr
import time
from gtts import gTTS


def speak(text: str):
    tts = gTTS(text=text, lang='pl')
    filename = 'voice.mp3'
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)


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
text = get_audio()
