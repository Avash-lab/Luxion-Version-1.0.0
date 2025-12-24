import time
import pyttsx3
import speech_recognition as sr
import eel
import sys
import os

def get_resource_path():
    """Get correct resource path for PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        return sys._MEIPASS
    else:
        # Running in normal Python environment
        return os.path.abspath(".")

def speak(text):
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        if len(voices) > 1:
            engine.setProperty('voice', voices[1].id)
        engine.setProperty('rate', 170)
        
        # Try to display message in UI
        try:
            eel.DisplayMessage(text)
        except:
            pass
        
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"⚠️  Text-to-speech error: {e}")
        # Fallback: print to console
        print(f"Luxion: {text}")

@eel.expose
def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Listening...')
        eel.DisplayMessage('Listening...')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, timeout=10, phrase_time_limit=6)
    
    try:
        print('Recognizing...')
        eel.DisplayMessage('Recognizing...')
        query = r.recognize_google(audio, language='en')
        print(f'User said: {query}')
        eel.DisplayMessage(query)
    except sr.WaitTimeoutError:
        print("Listening timed out")
        return ""
    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return ""
    except Exception as e:
        print(f"Error: {e}")
        return ""
    
    return query.lower()

@eel.expose
def allCommands():
    query = takeCommand()
    print(f"Query received: {query}")

    if not query or query == "":
        speak("I didn't hear anything. Please try again.")
        eel.ShowHood()
        return

    if 'open' in query:
        from engine.features import openCommand
        openCommand(query)

    elif 'close' in query:
        from engine.features import closeCommand
        closeCommand(query)

    elif 'youtube' in query and 'play' in query:
        from engine.features import PlayYoutube
        PlayYoutube(query)
    elif 'play' in query and ('youtube' in query or 'video' in query or 'song' in query):
        from engine.features import PlayYoutube
        PlayYoutube(query)

    elif 'time' in query and ('what' in query or 'tell' in query or 'current' in query):
        from engine.features import get_time
        get_time()

    elif 'date' in query and ('what' in query or 'today' in query or 'current' in query):
        from engine.features import get_date
        get_date()

    elif 'weather' in query or 'temperature' in query:
        from engine.features import get_weather
        get_weather(query)

    elif 'search' in query or 'google' in query:
        from engine.features import search_web
        search_web(query)

    elif 'news' in query or 'headlines' in query:
        from engine.features import get_news
        get_news()

    elif 'hello' in query or 'hi ' in query or 'hey ' in query:
        responses = [
            "Hello! How can I help you today?",
            "Hi there! What can I do for you?",
            "Hey! I'm ready to assist you.",
            "Hello! Nice to hear from you."
        ]
        import random
        speak(random.choice(responses))
        
    elif 'how are you' in query or "how're you" in query:
        responses = [
            "I'm doing great, thank you for asking!",
            "I'm functioning perfectly, ready to help you!",
            "I'm good, thanks! How about you?",
            "All systems operational! How can I assist you?"
        ]
        import random
        speak(random.choice(responses))
        
    elif 'your name' in query or "who are you" in query:
        speak("I'm your personal assistant created to help you with various tasks.")
        
    elif 'thank you' in query or 'thanks' in query:
        responses = [
            "You're welcome!",
            "My pleasure!",
            "Happy to help!",
            "Anytime! Is there anything else I can do for you?"
        ]
        import random
        speak(random.choice(responses))
        
    elif 'goodbye' in query or 'bye' in query or 'see you' in query:
        responses = [
            "Goodbye! Have a great day!",
            "See you later!",
            "Bye! Don't hesitate to call me if you need anything.",
            "Take care! I'll be here when you need me."
        ]
        import random
        speak(random.choice(responses))
        
    elif 'good morning' in query:
        speak("Good morning! Hope you have a wonderful day ahead!")
        
    elif 'good afternoon' in query:
        speak("Good afternoon! How's your day going?")
        
    elif 'good evening' in query:
        speak("Good evening! I hope you had a productive day.")
        
    elif 'good night' in query:
        speak("Good night! Sleep well and sweet dreams!")
        
    # JOKES
    elif 'joke' in query or 'funny' in query:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "What do you call a fake noodle? An impasta!",
            "Why did the bicycle fall over? Because it was two tired!",
            "What do you call a bear with no teeth? A gummy bear!"
        ]
        import random
        speak(random.choice(jokes))

    elif 'help' in query or 'what can you do' in query:
        help_message = """
        I can help you with many things! Here are some examples:
        - Open applications: Say 'open chrome'
        - Close applications: Say 'close chrome' or 'close all'
        - Play YouTube videos: Say 'play music on YouTube'
        - Tell time and date: Say 'what time is it' or 'what's the date today'
        - Search the web: Say 'search for artificial intelligence'
        - Get weather information: Say 'what's the weather like'
        - Get news headlines: Say 'give me the news'
        - Tell jokes: Say 'tell me a joke'
        - System controls: Say 'restart computer', 'shutdown', 'lock computer'
        And much more! Just ask and I'll try to help.
        """
        speak(help_message)

    elif 'shutdown' in query or 'turn off' in query:
        from engine.features import shutdown_computer
        shutdown_computer()
        
    elif 'restart' in query or 'reboot' in query:
        from engine.features import restart_computer
        restart_computer()
        
    elif 'sleep' in query or 'hibernate' in query:
        from engine.features import sleep_computer
        sleep_computer()
        
    elif 'lock' in query or 'lock computer' in query:
        from engine.features import lock_computer
        lock_computer()

    elif 'calculate' in query or 'what is' in query and any(op in query for op in ['plus', 'minus', 'times', 'divided by', '+', '-', '*', '/']):
        from engine.features import calculate_expression
        calculate_expression(query)

    elif 'remind' in query or 'reminder' in query:
        from engine.features import set_reminder
        set_reminder(query)
        
    # NOTE TAKING
    elif 'note' in query or 'write' in query:
        from engine.features import take_note
        take_note(query)

    elif 'volume' in query and ('up' in query or 'down' in query or 'mute' in query):
        from engine.features import control_volume
        control_volume(query)

    elif 'screenshot' in query or 'capture' in query:
        from engine.features import take_screenshot
        take_screenshot()

    elif 'wikipedia' in query or 'wiki' in query:
        from engine.features import search_wikipedia
        search_wikipedia(query)

    elif 'website' in query and 'open' in query:
        from engine.features import open_website
        open_website(query)

    elif 'system info' in query or 'system information' in query:
        from engine.features import get_system_info
        get_system_info()

    elif 'cpu' in query or 'memory' in query or 'ram' in query:
        from engine.features import get_cpu_usage, get_memory_usage
        if 'cpu' in query:
            get_cpu_usage()
        if 'memory' in query or 'ram' in query:
            get_memory_usage()

    elif 'create folder' in query or 'make folder' in query:
        from engine.features import create_folder
        create_folder(query)

    elif 'list files' in query or 'show files' in query:
        from engine.features import list_files
        list_files()

    elif any(word in query for word in ['what', 'how', 'why', 'who', 'when', 'where', 'explain']):
        from engine.features import answer_with_ollama
        answer_with_ollama(query)

    else:
        print('Command not recognized')
        responses = [
            "I'm not sure I understand. Could you please rephrase that?",
            "I didn't get that. Can you try saying it differently?",
            "Sorry, I don't know how to help with that yet.",
            "I'm still learning. Could you try a different command?"
        ]
        import random
        speak(random.choice(responses))

    eel.ShowHood()