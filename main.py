from vosk import Model, KaldiRecognizer  # оффлайн-распознавание от Vosk
import speech_recognition  # распознавание пользовательской речи (Speech-To-Text)
import pyttsx3  # синтез речи (Text-To-Speech)
import wave  # создание и чтение аудиофайлов формата wav
import json  # работа с json-файлами и json-строками
import os  # работа с файловой системой
import requests
from bs4 import BeautifulSoup


class VoiceAssistant:
    """
    Настройки голосового ассистента, включающие имя, пол, язык речи
    """
    name = ""
    sex = ""
    speech_language = ""
    recognition_language = ""


def setup_assistant_voice():
    """
    Установка голоса по умолчанию (индекс может меняться в
    зависимости от настроек операционной системы)
    """
    voices = ttsEngine.getProperty("voices")

    if assistant.speech_language == "en":
        assistant.recognition_language = "en-US"
        if assistant.sex == "female":
            # Microsoft Zira Desktop - English (United States)
            ttsEngine.setProperty("voice", voices[16].id)
        else:
            # Microsoft David Desktop - English (United States)
            ttsEngine.setProperty("voice", voices[11].id)
    else:
        assistant.recognition_language = "ru-RU"
        # Microsoft Irina Desktop - Russian
        # ttsEngine.setProperty("voice", voices[56].id)
        ttsEngine.setProperty("voice", 'ru')


def get_html(url):
    r = requests.get(url)    # Получим метод Response
    r.encoding = 'utf8'
    return r.text   # Вернем данные объекта text



def get_info():
    html = get_html('https://ria.ru/lenta')
    soup = BeautifulSoup(html, 'lxml')
    head = soup.find('div', id='widgetLenta')
    lines = head.text.split(':')
    data=[]
    for i in lines:
        data.append(i[2:-2])
    del data[20]
    del data[0]
    return data

def say_text(voice_assistant: VoiceAssistant):
    text = get_text()
    k = 0
    count = 5
    while k < count:
        print(text[k])
        say(voice_assistant, ru=text[k])
        k += 1
    say(voice_assistant, ru='Ещё?')

def say_text1(voice_assistant: VoiceAssistant):
    text = get_text()
    k = 5
    count = 10
    while k < count:
        print(text[k])
        say(voice_assistant, ru=text[k])
        k += 1


def get_text():
    text = get_info()
    return text

def say(voice_assistant: VoiceAssistant, **kwargs):
    if voice_assistant.speech_language == "en":
        ttsEngine.say(kwargs['en'])
        ttsEngine.runAndWait()
    else:
        ttsEngine.say(kwargs['ru'])
        ttsEngine.runAndWait()


def exit_program(voice_assistant:VoiceAssistant, *args):
    if len(args):
        exit(args[0])
    else:
        exit(1)


def record_and_recognize_audio(*args: tuple):
    """
    Запись и распознавание аудио
    """
    with microphone:
        recognized_data = ""

        # регулирование уровня окружающего шума
        recognizer.adjust_for_ambient_noise(microphone, duration=2)

        try:
            print("Listening...")
            audio = recognizer.listen(microphone, 5, 5)

            with open("microphone-results.wav", "wb") as file:
                file.write(audio.get_wav_data())

        except speech_recognition.WaitTimeoutError:
            print("Can you check if your microphone is on, please?")
            return

        # использование online-распознавания через Google
        # (высокое качество распознавания)
        try:
            print("Started recognition...")
            recognized_data = recognizer.recognize_google(audio, language="ru").lower()

        except speech_recognition.UnknownValueError:
            pass

        # в случае проблем с доступом в Интернет происходит
        # попытка использовать offline-распознавание через Vosk
        except speech_recognition.RequestError:
            print("Trying to use offline recognition...")
            recognized_data = use_offline_recognition()

        return recognized_data


def use_offline_recognition():
    """
    Переключение на оффлайн-распознавание речи
    :return: распознанная фраза
    """
    recognized_data = ""
    try:
        # проверка наличия модели на нужном языке в каталоге приложения
        if not os.path.exists("models/vosk-model-small-ru-0.15"):
            print("Please download the model from:\n"
                  "https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
            exit(1)

        # анализ записанного в микрофон аудио (чтобы избежать повторов фразы)
        wave_audio_file = wave.open("microphone-results.wav", "rb")
        model = Model("models/vosk-model-small-ru-0.15")
        offline_recognizer = KaldiRecognizer(model, wave_audio_file.getframerate())

        data = wave_audio_file.readframes(wave_audio_file.getnframes())
        if len(data) > 0:
            if offline_recognizer.AcceptWaveform(data):
                recognized_data = offline_recognizer.Result()

                # получение данных распознанного текста из JSON-строки
                # (чтобы можно было выдать по ней ответ)
                recognized_data = json.loads(recognized_data)
                recognized_data = recognized_data["text"]
    except:
        print("Sorry, speech service is unavailable. Try again later")

    return recognized_data


def execute_command_with_name(command_name: str, voice_assistant: VoiceAssistant, *args: list):
    """
    Выполнение заданной пользователем команды и аргументами
    :param voice_assistant:
    :param command_name: название команды
    :param args: аргументы, которые будут переданы в метод
    :return:
    """

    commands = {
        ("новости", "покажи новости", "информация", "расскажи новости","news"): say_text,
        ("ещё", "да"): say_text1,
        ("закрыть программу", "закрой программу", "выйти", "выйти из программы", "exit", "exit program"): exit_program
    }

    for key in commands.keys():
        if command_name in key:
            commands[key](voice_assistant, *args)
        else:
            pass  # print("Command not found")


if __name__ == "__main__":

    # инициализация инструментов распознавания и ввода речи
    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()

    # инициализация инструмента синтеза речи
    ttsEngine = pyttsx3.init()

    # настройка данных голосового помощника
    assistant = VoiceAssistant()
    assistant.name = "Vlad"
    assistant.sex = "male"
    assistant.speech_language = "ru"

    # установка голоса по умолчанию
    setup_assistant_voice()

    while True:
        # старт записи речи с последующим выводом распознанной речи
        # и удалением записанного в микрофон аудио
        voice_input = record_and_recognize_audio()
        os.remove("microphone-results.wav")
        print(voice_input)

        # отделение комманд от дополнительной информации (аргументов)
        # voice_input = voice_input.split(" ")
        command = voice_input
        # command_options = [str(input_part) for input_part in voice_input[1:len(voice_input)]]
        execute_command_with_name(command, assistant)
