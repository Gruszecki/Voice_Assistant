import pyttsx3
import speech_recognition as sr

def speak(text: str):
    engine = pyttsx3.init()
    engine.setProperty('rate', 175)
    engine.say(text)
    engine.runAndWait()

def get_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source)

        try:
            said = recognizer.recognize_google(audio, language='pl-PL')
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio.")
            return 'NOT UNDERSTOOD'
        except sr.RequestError as e:
            print('Could not request results from Google Speech Recognition service:', str(e))
            return 'ERROR'

    return said.lower()