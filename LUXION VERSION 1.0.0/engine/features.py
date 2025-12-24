import os
import re
import sqlite3
import webbrowser
import psutil
import subprocess
import datetime
import time
import requests
import json
import pyautogui
import pyperclip
import platform
import random
from playsound import playsound
import eel
from bs4 import BeautifulSoup
import wikipedia
import sys

from engine.command import speak
import pywhatkit as kit
from dotenv import load_dotenv
load_dotenv()

conn = sqlite3.connect("sophia.db")
cursor = conn.cursor()

def resource_path(relative_path):
    """ Get absolute path to resource for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def start_ollama_if_not_running():
    """Check if Ollama is running, start it if not"""
    print("Checking if Luxion is running...")
    
    # Check if Ollama process is running
    ollama_running = False
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and 'ollama' in proc.info['name'].lower():
                ollama_running = True
                print("✅ Luxion is already running")
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if not ollama_running:
        print("🔄 Starting Ollama...")
        try:
            # Try different methods to start Ollama
            methods = [
                # Method 1: Start as service
                ['net', 'start', 'Ollama'],
                # Method 2: Run executable from Program Files
                ['C:\\Program Files\\Ollama\\ollama.exe', 'serve'],
                # Method 3: Start from default location
                [os.path.expanduser('~\\AppData\\Local\\Programs\\Ollama\\ollama.exe'), 'serve'],
                # Method 4: Use ollama command if in PATH
                ['ollama', 'serve']
            ]
            
            for method in methods:
                try:
                    # Check if the executable exists for methods 2 and 3
                    if method[0].endswith('.exe') and not os.path.exists(method[0]):
                        print(f"   Skipping {method[0]} - not found")
                        continue
                    
                    print(f"   Trying: {' '.join(method)}")
                    process = subprocess.Popen(
                        method,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        text=True
                    )
                    
                    # Check if it started successfully
                    time.sleep(3)
                    if process.poll() is None:  # Process is still running
                        print(f"✅ Started Ollama using: {' '.join(method)}")
                        
                        # Wait a bit more for full startup
                        print("   Waiting for Ollama to initialize...")
                        time.sleep(5)
                        return True
                    else:
                        # Process ended quickly (error)
                        stdout, stderr = process.communicate()
                        print(f"   ❌ Process ended: {stderr}")
                        
                except FileNotFoundError:
                    print(f"   ❌ Command not found: {method[0]}")
                    continue
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    continue
                    
            print("❌ Could not start Ollama using any method")
            print("   Please install Ollama from https://ollama.com")
            return False
            
        except Exception as e:
            print(f"❌ Error starting Ollama: {e}")
            return False
    
    return True

def playAssistantSound():
    """Play startup sound"""
    try:
        sound_paths = [
            resource_path(os.path.join("www", "assets", "audio", "activation.mp3")),
            os.path.join("www", "assets", "audio", "activation.mp3"),
            "www/assets/audio/activation.mp3",
            "activation.mp3"
        ]
        
        for sound_path in sound_paths:
            if os.path.exists(sound_path):
                playsound(sound_path)
                return
        
        print("⚠️  Startup sound not found")
    except Exception as e:
        print(f"⚠️  Could not play startup sound: {e}")


@eel.expose
def playClickSound():
    music_dir = ""
    playsound(music_dir)
 

def openCommand(query):

    query = query.replace("open", "").strip().lower()
    
    if query != "":
        try:

            cursor.execute('SELECT path FROM sys_command WHERE LOWER(name) = ?', (query,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak(f"Opening {query}")
                os.startfile(results[0][0])
                return

            cursor.execute('SELECT url FROM web_command WHERE LOWER(name) = ?', (query,))
            results = cursor.fetchall()
            
            if len(results) != 0:
                speak(f"Opening {query}")
                webbrowser.open(results[0][0])
                return

            speak(f"Opening {query}")

            app_mappings = {
                'discord': ['C:\\Users\\%USERNAME%\\AppData\\Local\\Discord\\app-*\\Discord.exe',
                           'C:\\Program Files\\Discord\\Discord.exe',
                           os.path.expanduser('~\\AppData\\Local\\Discord\\Update.exe')],
                
                'chrome': ['C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
                          'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'],
                
                'firefox': ['C:\\Program Files\\Mozilla Firefox\\firefox.exe',
                           'C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe'],
                
                'edge': ['C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'],
                
                'spotify': ['C:\\Users\\%USERNAME%\\AppData\\Roaming\\Spotify\\Spotify.exe',
                           'C:\\Program Files\\WindowsApps\\SpotifyAB.SpotifyMusic_*\\Spotify.exe'],
                
                'whatsapp': ['C:\\Users\\%USERNAME%\\AppData\\Local\\WhatsApp\\WhatsApp.exe'],
                
                'telegram': ['C:\\Users\\%USERNAME%\\AppData\\Roaming\\Telegram Desktop\\Telegram.exe'],
                
                'steam': ['C:\\Program Files (x86)\\Steam\\Steam.exe'],
                
                'vscode': ['C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe'],
                
                'notepad': ['notepad.exe'],
                
                'calculator': ['calc.exe'],
                
                'cmd': ['cmd.exe'],
                
                'powershell': ['powershell.exe'],
                
                'paint': ['mspaint.exe'],
                
                'word': ['C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.exe'],
                
                'excel': ['C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.exe'],
                
                'powerpoint': ['C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.exe'],
            }

            if query in app_mappings:
                for path_pattern in app_mappings[query]:
                    try:

                        if '%USERNAME%' in path_pattern:
                            path_pattern = path_pattern.replace('%USERNAME%', os.getlogin())

                        if '*' in path_pattern:
                            import glob
                            matches = glob.glob(path_pattern)
                            if matches:
                                os.startfile(matches[0])
                                return
                        else:
                            os.startfile(path_pattern)
                            return
                    except:
                        continue

            try:
                os.system(f'start "" "{query}"')
                return
            except:
                pass
                
            speak(f"I couldn't find {query}. Please add it to the database or check if it's installed.")
            
        except Exception as e:
            speak(f"Something went wrong: {str(e)}")


def closeCommand(query):
    """
    Close applications based on the query
    Supports: close [app_name], close all, close current
    """
    query = query.replace("close", "").strip().lower()
    
    if not query:
        speak("Please specify what to close.")
        return
    
    try:

        if query == "all" or query == "everything":
            closeAllApplications()
            return
        elif query == "current" or query == "this" or query == "active":
            closeCurrentApplication()
            return
        elif query == "browser" or query == "web browser":
            closeSpecificApplication("chrome")
            return
        elif query == "music" or query == "player":
            closeSpecificApplication("spotify")
            return
        elif query == "video" or query == "media":
            closeSpecificApplication("vlc")
            return

        closeSpecificApplication(query)
        
    except Exception as e:
        speak(f"Something went wrong while trying to close applications: {str(e)}")


def get_process_names(app_name):
    """Get process names based on application name"""

    process_mappings = {
        'chrome': ['chrome.exe'],
        'firefox': ['firefox.exe'],
        'edge': ['msedge.exe'],
        'notepad': ['notepad.exe'],
        'calculator': ['calculator.exe'],
        'word': ['winword.exe'],
        'excel': ['excel.exe'],
        'powerpoint': ['powerpnt.exe'],
        'vscode': ['code.exe'],
        'pycharm': ['pycharm.exe', 'pycharm64.exe'],
        'spotify': ['spotify.exe'],
        'discord': ['discord.exe'],
        'whatsapp': ['whatsapp.exe'],
        'teams': ['teams.exe'],
        'onenote': ['onenote.exe'],
        'cmd': ['cmd.exe'],
        'terminal': ['cmd.exe', 'powershell.exe', 'wt.exe'],
        'powershell': ['powershell.exe'],
        'task manager': ['taskmgr.exe'],
        'file explorer': ['explorer.exe'],
        'photoshop': ['photoshop.exe'],
        'illustrator': ['illustrator.exe'],
        'premiere': ['premiere.exe'],
        'after effects': ['afterfx.exe'],
        'vlc': ['vlc.exe'],
        'media player': ['wmplayer.exe'],
        'snipping tool': ['snippingtool.exe'],
        'paint': ['mspaint.exe'],
        'outlook': ['outlook.exe'],
        'skype': ['skype.exe'],
        'zoom': ['zoom.exe'],
        'steam': ['steam.exe'],
        'epic games': ['epicgameslauncher.exe'],
        'obs': ['obs64.exe', 'obs.exe'],
        'slack': ['slack.exe'],
        'telegram': ['telegram.exe'],
        'signal': ['signal.exe'],
        'brave': ['brave.exe'],
        'opera': ['opera.exe'],
        'safari': ['safari.exe'],
        'photos': ['microsoft.photos.exe'],
        'camera': ['windowscamera.exe'],
        'calendar': ['outlookcal.exe'],
        'mail': ['hxmail.exe', 'outlook.exe'],
        'store': ['winstore.app.exe'],
        'settings': ['systemsettings.exe'],
        'control panel': ['control.exe'],
        'wordpad': ['wordpad.exe'],
        'sticky notes': ['stikynot.exe'],
        'alarm': ['alarms.exe'],
        'clock': ['alarms.exe'],
        'weather': ['bingweather.exe'],
        'news': ['bingnews.exe'],
        'cortana': ['searchui.exe'],
        'windows search': ['searchui.exe'],
        'task view': ['taskview.exe'],
        'action center': ['actioncenter.exe'],
        'xbox': ['xboxapp.exe'],
        'game bar': ['gamebar.exe'],
        'movies': ['zunevideo.exe'],
        'groove music': ['groovemusic.exe'],
        'voice recorder': ['soundrecorder.exe'],
        'people': ['people.exe'],
        'phone': ['phone.exe'],
        'todo': ['todo.exe'],
        'whiteboard': ['whiteboard.exe'],
        'solitaire': ['solitaire.exe'],
        'minesweeper': ['minesweeper.exe'],
        'sudoku': ['sudoku.exe'],
        'chess': ['chess.exe'],
    }
    
    if app_name in process_mappings:
        return process_mappings[app_name]
    else:

        return [app_name + '.exe']


def close_processes_by_name(process_names, app_name):
    """Close processes by their names"""
    closed = False
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc_name = proc.info['name'].lower() if proc.info['name'] else ""
            
            for target_name in process_names:
                if target_name in proc_name:
                    pid = proc.info['pid']
                    p = psutil.Process(pid)

                    critical_processes = ['explorer.exe', 'svchost.exe', 'csrss.exe', 'wininit.exe', 
                                         'services.exe', 'lsass.exe', 'taskhost.exe', 'sihost.exe',
                                         'eel.exe', 'python.exe', 'pythonw.exe']
                    
                    if proc_name in critical_processes:
                        speak(f"Cannot close system process: {app_name}")
                        return True

                    try:
                        p.terminate()
                        speak(f"Closing {app_name}")
                        closed = True
                        return True
                    except:

                        try:
                            p.kill()
                            speak(f"Forced closing {app_name}")
                            closed = True
                            return True
                        except:
                            continue
                            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    if not closed:

        for target_name in process_names:
            try:

                result = subprocess.run(['taskkill', '/im', target_name], 
                                      capture_output=True, shell=True, text=True)
                
                if result.returncode == 0 or "success" in result.stdout.lower():
                    speak(f"Closing {app_name}")
                    return True
                else:

                    result = subprocess.run(['taskkill', '/f', '/im', target_name], 
                                          capture_output=True, shell=True, text=True)
                    if result.returncode == 0 or "success" in result.stdout.lower():
                        speak(f"Force closing {app_name}")
                        return True
                        
            except Exception as e:
                print(f"Taskkill error for {target_name}: {e}")
                continue
    
    return False


def closeSpecificApplication(app_name):
    """
    Close a specific application by name
    """

    try:

        cursor.execute("PRAGMA table_info(sys_command)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        process_names = []
        
        if 'process_name' in column_names:
            cursor.execute('SELECT process_name FROM sys_command WHERE LOWER(name) = ?', (app_name,))
            results = cursor.fetchall()
            if len(results) != 0 and results[0][0]:

                process_names = [results[0][0].lower()]
            else:
                process_names = get_process_names(app_name)
        else:
            process_names = get_process_names(app_name)
            
    except Exception as e:
        print(f"Database error: {e}")
        process_names = get_process_names(app_name)

    closed = close_processes_by_name(process_names, app_name)
    
    if not closed:

        if app_name not in ['all', 'current', 'this', 'active', 'everything', 'browser', 'music', 'video', 'media', 'player']:
            speak(f"Could not find {app_name} running or it's already closed.")
        return False
    
    return True


def closeAllApplications():
    """
    Close all non-essential applications
    """

    system_processes = [
        'svchost.exe', 'explorer.exe', 'dwm.exe', 
        'csrss.exe', 'wininit.exe', 'services.exe',
        'lsass.exe', 'taskhost.exe', 'sihost.exe',
        'ctfmon.exe', 'dllhost.exe', 'smss.exe',
        'eel.exe', 'python.exe', 'pythonw.exe'
    ]
    
    closed_count = 0
    speak("Closing all non-essential applications")
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc_name = proc.info['name'].lower() if proc.info['name'] else ""

            if proc_name in system_processes:
                continue

            if not proc_name:
                continue

            if any(sys_proc in proc_name for sys_proc in system_processes):
                continue
            
            pid = proc.info['pid']
            p = psutil.Process(pid)

            try:
                p.terminate()
                closed_count += 1
            except:

                try:
                    p.kill()
                    closed_count += 1
                except:
                    pass
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    speak(f"Closed {closed_count} applications")


def closeCurrentApplication():
    """
    Close the currently active/focused application
    """
    try:
        import win32gui
        import win32process
        

        hwnd = win32gui.GetForegroundWindow()
        
        if hwnd:

            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            

            process = psutil.Process(pid)
            app_name = process.name()

            system_processes = ['explorer.exe', 'dwm.exe', 'taskhost.exe', 'sihost.exe']
            
            if app_name.lower() in system_processes:
                speak("Cannot close system application")
                return

            try:
                process.terminate()
                speak(f"Closing current application: {app_name.replace('.exe', '')}")
            except:
                try:
                    process.kill()
                    speak(f"Forced closing current application: {app_name.replace('.exe', '')}")
                except Exception as e:
                    speak("Could not close the current application")
        else:
            speak("No active application found")
            
    except ImportError:
        speak("Required modules not installed. Please install pywin32")
    except Exception as e:
        speak("Could not close the current application")
        print(f"Error: {e}")


def PlayYoutube(query):
    search_term = extract_yt_term(query)
    if search_term:
        speak(f"Playing {search_term} on YouTube")
        kit.playonyt(search_term)
    else:
        speak("Sorry, I couldn't find what to play on YouTube.")


def extract_yt_term(command):
    patterns = [
        r'play\s+(.*?)\s+on\s+youtube',
        r'play\s+(.*?)\s+in\s+youtube',
        r'youtube\s+play\s+(.*)',
        r'play\s+(.*)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None


def get_time():
    """Get current time"""
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The current time is {current_time}")


def get_date():
    """Get current date"""
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    speak(f"Today's date is {current_date}")


def get_weather(query=None):
    """Get weather information"""
    try:

        location = "your location"
        if query:

            if 'in ' in query:
                location = query.split('in ')[-1]
            elif 'at ' in query:
                location = query.split('at ')[-1]
        

        speak(f"I'm checking the weather in {location}. For accurate weather, you might want to check a weather website.")
    
    except Exception as e:
        speak("Sorry, I couldn't check the weather at the moment.")
        print(f"Weather error: {e}")


def search_web(query):
    """Search the web"""
    search_term = query.replace("search", "").replace("for", "").replace("google", "").strip()
    if search_term:
        speak(f"Searching for {search_term}")
        webbrowser.open(f"https://www.google.com/search?q={search_term}")
    else:
        speak("What would you like me to search for?")


def get_news():
    """Get news headlines"""
    try:
        speak("Getting the latest news headlines")

        url = "https://feeds.bbci.co.uk/news/rss.xml"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')[:5]
        
        headlines = []
        for item in items:
            title = item.title.text
            headlines.append(title)
        
        speak("Here are the top news headlines:")
        for i, headline in enumerate(headlines, 1):
            speak(f"{i}. {headline}")
            
    except Exception as e:
        speak("Sorry, I couldn't fetch the news at the moment.")


def calculate_expression(query):
    """Calculate mathematical expressions"""
    try:

        expression = query.replace("calculate", "").replace("what is", "").strip()
        

        expression = expression.replace("plus", "+").replace("minus", "-").replace("times", "*").replace("divided by", "/")

        result = eval(expression)
        speak(f"The result is {result}")
        
    except Exception as e:
        speak("Sorry, I couldn't calculate that expression.")


def set_reminder(query):
    """Set a reminder"""
    speak("Reminder feature is under development. For now, you can say 'remind me to [task]' and I'll make a note of it.")

    reminder_text = query.replace("remind me to", "").replace("remind me", "").replace("reminder", "").strip()
    

    with open("reminders.txt", "a") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp}: {reminder_text}\n")
    
    speak(f"I've noted your reminder: {reminder_text}")


def take_note(query):
    """Take a note"""
    note_text = query.replace("note", "").replace("write", "").replace("take a", "").strip()
    
    if note_text:

        with open("notes.txt", "a") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp}: {note_text}\n")
        
        speak("I've saved your note.")
    else:
        speak("What would you like me to note down?")


def control_volume(query):
    """Control system volume"""
    try:
        if 'mute' in query or 'silent' in query:
            speak("Muting volume")
            os.system("nircmd.exe mutesysvolume 2")
        elif 'unmute' in query or 'sound on' in query:
            speak("Unmuting volume")
            os.system("nircmd.exe mutesysvolume 2")
        elif 'up' in query or 'increase' in query:
            speak("Increasing volume")
            os.system("nircmd.exe changesysvolume 2000")
        elif 'down' in query or 'decrease' in query:
            speak("Decreasing volume")
            os.system("nircmd.exe changesysvolume -2000")
        else:
            speak("Volume control command not recognized")
    except:
        speak("Could not control volume. Make sure nircmd is installed.")


def take_screenshot():
    """Take a screenshot and save to Screenshots folder"""
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"

        screenshots_dir = "Screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
        
        filepath = os.path.join(screenshots_dir, filename)
        
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        
        speak(f"Screenshot saved to Screenshots folder as {filename}")
    except Exception as e:
        speak("Sorry, I couldn't take a screenshot.")


def search_wikipedia(query):
    """Search Wikipedia"""
    try:
        search_term = query.replace("wikipedia", "").replace("search", "").strip()
        if search_term:
            result = wikipedia.summary(search_term, sentences=2)
            speak(f"According to Wikipedia: {result}")
        else:
            speak("What would you like me to search on Wikipedia?")
    except:
        speak("Sorry, I couldn't find that on Wikipedia.")


def tell_joke():
    """Tell a random joke"""
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "What do you call a fake noodle? An impasta!",
        "Why did the bicycle fall over? Because it was two tired!",
        "What do you call a bear with no teeth? A gummy bear!",
        "Why don't eggs tell jokes? They'd crack each other up!",
        "What do you call a sleeping dinosaur? A dino-snore!",
        "Why did the tomato turn red? Because it saw the salad dressing!",
        "What do you get when you cross a snowman and a vampire? Frostbite!",
        "Why did the computer go to the doctor? Because it had a virus!"
    ]
    joke = random.choice(jokes)
    speak(joke)


def get_system_info():
    """Get system information"""
    try:
        system = platform.system()
        version = platform.version()
        processor = platform.processor()
        speak(f"You're running {system} version {version} with {processor} processor.")
    except:
        speak("I can't retrieve system information at the moment.")


def open_website(query):
    """Open a specific website"""
    site = query.replace("open", "").replace("website", "").strip()
    
    if site:

        cursor.execute('SELECT url FROM web_command WHERE LOWER(name) = ?', (site,))
        results = cursor.fetchall()
        
        if len(results) != 0:
            speak(f"Opening {site}")
            webbrowser.open(results[0][0])
        else:

            websites = {
                'youtube': 'https://youtube.com',
                'facebook': 'https://facebook.com',
                'twitter': 'https://twitter.com',
                'instagram': 'https://instagram.com',
                'linkedin': 'https://linkedin.com',
                'github': 'https://github.com',
                'gmail': 'https://gmail.com',
                'google': 'https://google.com',
                'amazon': 'https://amazon.com',
                'netflix': 'https://netflix.com',
                'whatsapp': 'https://web.whatsapp.com',
                'discord': 'https://discord.com'
            }
            
            if site in websites:
                speak(f"Opening {site}")
                webbrowser.open(websites[site])
            else:

                if not site.startswith('http'):
                    site = 'https://' + site
                speak(f"Opening {site}")
                webbrowser.open(site)
    else:
        speak("Which website would you like to open?")


def create_folder(query):
    """Create a new folder"""
    folder_name = query.replace("create folder", "").replace("make folder", "").strip()
    
    if folder_name:
        try:
            os.mkdir(folder_name)
            speak(f"Created folder named {folder_name}")
        except Exception as e:
            speak(f"Could not create folder: {str(e)}")
    else:
        speak("What should I name the folder?")


def list_files():
    """List files in current directory"""
    files = os.listdir('.')
    if files:
        speak(f"There are {len(files)} files and folders here.")
        for i, file in enumerate(files[:5], 1):
            speak(f"{i}. {file}")
        if len(files) > 5:
            speak("... and more")
    else:
        speak("This directory is empty.")


def get_cpu_usage():
    """Get CPU usage"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        speak(f"Current CPU usage is {cpu_percent} percent")
    except:
        speak("Could not retrieve CPU information")


def get_memory_usage():
    """Get memory usage"""
    try:
        memory = psutil.virtual_memory()
        used_gb = memory.used / (1024 ** 3)
        total_gb = memory.total / (1024 ** 3)
        percent = memory.percent
        
        speak(f"Memory usage: {used_gb:.1f} GB out of {total_gb:.1f} GB, which is {percent} percent")
    except:
        speak("Could not retrieve memory information")


def restart_computer():
    """Restart the computer"""
    speak("Restarting computer in 10 seconds. Please save your work.")
    time.sleep(10)
    os.system("shutdown /r /t 1")


def shutdown_computer():
    """Shutdown the computer"""
    speak("Shutting down computer in 10 seconds. Please save your work.")
    time.sleep(10)
    os.system("shutdown /s /t 1")


def lock_computer():
    """Lock the computer"""
    speak("Locking computer")
    os.system("rundll32.exe user32.dll,LockWorkStation")


def sleep_computer():
    """Put computer to sleep"""
    speak("Putting computer to sleep")
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def answer_with_ollama(question):
    """
    Uses local Ollama for AI responses - FIXED VERSION
    """
    import requests
    import json
    from engine.command import speak
    
    print(f"🤖 Processing: {question}")
    
    try:
        # First check if we can connect to Ollama
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code != 200:
                speak("Ollama server is not responding. Starting it now...")
                # Try to start Ollama
                import subprocess
                subprocess.Popen(['ollama', 'serve'], 
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
                import time
                time.sleep(5)  # Wait for server to start
        except requests.exceptions.ConnectionError:
            speak("Starting Ollama server...")
            import subprocess
            subprocess.Popen(['ollama', 'serve'], 
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
            import time
            time.sleep(5)
        
        # Now try to get available models
        try:
            models_response = requests.get("http://localhost:11434/api/tags", timeout=10)
            if models_response.status_code == 200:
                models_data = models_response.json()
                available_models = [model['name'] for model in models_data.get('models', [])]
                
                if not available_models:
                    speak("No AI models found. Please run: ollama pull phi")
                    return
                
                # Use the first available model
                model_to_use = available_models[0]
                print(f"   Using model: {model_to_use}")
            else:
                # Fallback to phi
                model_to_use = "phi"
        except:
            model_to_use = "phi"  # Default fallback
        
        # Generate response
        speak("Thinking...")
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                "model": model_to_use,
                "prompt": f"You are a helpful assistant. Answer this concisely: {question}",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 150
                }
            },
            timeout=30  # Increased timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result['response'].strip()
            print(f"✅ Answer: {answer[:100]}...")
            speak(answer)
        else:
            speak("I couldn't generate a response. The model might need to be downloaded.")
            print(f"❌ API Error: {response.status_code}")
            
    except requests.exceptions.Timeout:
        speak("The AI is taking too long to respond. Try a simpler question.")
        print("⚠️  Request timeout")
    except Exception as e:
        speak("There was an error with the AI system.")
        print(f"❌ Error: {e}")

def find_installed_apps(app_name):
    """Try to find installed applications in common locations"""
    common_paths = [

        'C:\\Program Files\\',
        'C:\\Program Files (x86)\\',

        os.path.expanduser('~\\AppData\\Local\\'),
        os.path.expanduser('~\\AppData\\Roaming\\'),
        os.path.expanduser('~\\AppData\\Local\\Programs\\'),

        'C:\\Program Files\\WindowsApps\\',
    ]
    
    search_patterns = [
        f'*{app_name}*.exe',
        f'{app_name}.exe',
        f'{app_name}*.exe',
    ]
    
    import glob
    
    for base_path in common_paths:
        for pattern in search_patterns:
            try:
                full_pattern = os.path.join(base_path, '**', pattern)
                matches = glob.glob(full_pattern, recursive=True)

                valid_matches = []
                for match in matches:
                    if 'uninstall' not in match.lower() and 'install' not in match.lower():
                        valid_matches.append(match)
                
                if valid_matches:
                    return valid_matches[0] 
            except:
                continue
    
    return None