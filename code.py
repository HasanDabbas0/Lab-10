import json
import requests
import os
import pyttsx3
import pyaudio
import vosk
import webbrowser
from vosk import KaldiRecognizer


class VoiceAssistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.tts = pyttsx3.init('sapi5')

        model_folder = r"C:\Users\mi\Downloads\vosk-model-small-en-us-0.15"
        self.model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), model_folder)

        if not os.path.exists(self.model_path):
            print(f"Model {self.model_path} not found.")
            exit(1)

        self.model = vosk.Model(self.model_path)
        self.rec = KaldiRecognizer(self.model, 16000)
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
        self.stream.start_stream()

    def get_word_meaning(self, word):
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def save_to_file(self, data):
        with open("saved_data.txt", "a") as file:
            file.write(data + "\n")
        self.speak("Data has been saved successfully.")

    def handle_command(self, command):
        if command.startswith("find"):
            word = command.split("find")[1].strip()
            self.current_word = word
            self.word_meaning = self.get_word_meaning(word)
            if self.word_meaning:
                self.speak(f"The word {self.current_word} is found. Please, let me know what you want to know about it: "
                           f"'meaning', 'link', or 'save'.")
            else:
                self.speak("Please start by saying the word you want to learn, like 'find word'.")

        elif command == "save":
            self.speak("Saving your data...")
            if hasattr(self, 'current_word'):
                self.save_to_file(self.current_word)
            else:
                self.speak("Please start by saying the word you want to learn, like 'find word'.")

        elif command == "meaning":
            if hasattr(self, 'word_meaning') and self.word_meaning:
                meanings = self.word_meaning[0]['meanings']
                for meaning in meanings:
                    part_of_speech = meaning['partOfSpeech']
                    definition = meaning['definitions'][0]['definition']
                    self.speak(f"{self.current_word}, {part_of_speech}: {definition}")
            else:
                self.speak("Please start by saying the word you want to learn, like 'find word'.")

        elif command.startswith("link"):
            if hasattr(self, 'current_word'):
                url = f"https://dictionary.cambridge.org/dictionary/english/{self.current_word}"
                webbrowser.open(url)
                self.speak("Opening information in your browser.")
            else:
                self.speak("Please start by saying the word you want to learn, like 'find word'.")

        elif command == "example":
            self.speak("For example: 'find hedgehog'")

        elif command == "exit":
            self.speak("Finishing the work... Goodbye!")
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
        else:
            self.speak("Sorry, I didn't understand that command.")

    def start(self):
        print("Listening...")
        while True:
            data = self.stream.read(4096, exception_on_overflow=False)
            if self.rec.AcceptWaveform(data):
                result = self.rec.Result()
                result_dict = json.loads(result)
                command = result_dict.get("text", "").strip().lower()
                if command:
                    print(f"Command: {command}")
                    self.handle_command(command)
                else:
                    print("No command recognized.")
            else:
                partial_result = self.rec.PartialResult()
                print(partial_result)


if __name__ == '__main__':
    assistant = VoiceAssistant()
    assistant.start()
