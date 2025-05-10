import pyttsx3
import speech_recognition as sr
import datetime
import requests
import pyjokes
import os
import subprocess
import platform
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk
import threading
import webbrowser
from pytube import Search
from pygame import mixer
import geocoder
import socket
import logging
import config

logging.basicConfig(filename='luna.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

engine = pyttsx3.init()
mixer.init()

window = tk.Tk()
window.title("Luna - Virtual Assistant")
window.geometry("400x600")
window.configure(bg='black')

image = Image.open("assets\\luna.jpeg")
image = image.resize((400, 400), Image.Resampling.LANCZOS)
photo = ImageTk.PhotoImage(image)
img_label = Label(window, image=photo, bg='black')
img_label.pack(pady=10)
img_label.image = photo

response_label = Label(window, text="Hello! I am Luna.", font=("Arial", 14), wraplength=500, fg='white', bg='black')
response_label.pack(pady=20)

status_label = Label(window, text="Listening Status: Not Listening", font=("Arial", 12), fg='white', bg='black')
status_label.pack(pady=10)

engine = pyttsx3.init()
voices = engine.getProperty('voices')

# List of common female voice indicators across OSes
female_keywords = ["zira", "samantha", "victoria", "karen", "fiona", "female", "f3", "f4"]

# Try to find a female voice
for voice in voices:
    voice_name = voice.name.lower()
    if any(keyword in voice_name for keyword in female_keywords):
        engine.setProperty('voice', voice.id)
        logging.info(f"Female voice set: {voice.name}")
        break
else:
    logging.warning("Female voice not found, using default voice.")

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        update_status("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        logging.info(f"Command: {command}")
        update_status("Not Listening")
        return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't understand that.")
        update_status("Not Listening")
        return ""
    except sr.RequestError:
        speak("Network error. Please try again later.")
        update_status("Not Listening")
        return ""

def update_status(status):
    status_label.config(text=f"Listening Status: {status}")
    window.update_idletasks()

def play_online_video(video_name):
    try:
        search = Search(video_name)
        results = search.results
        if results:
            video_url = f"https://www.youtube.com/watch?v={results[0].video_id}"
            webbrowser.open(video_url)
            speak(f"Playing {video_name} on YouTube.")
        else:
            speak("I couldn't find the video online.")
    except Exception as e:
        logging.error(f"Error playing online video: {e}")
        speak(f"An error occurred while searching for the video online. {str(e)}")

def play_offline_video(video_name):
    try:
        video_dir = "C:\\Users\\Rizve\\Videos"
        for root, dirs, files in os.walk(video_dir):
            for file in files:
                if video_name.lower() in file.lower() and file.endswith((".mp4", ".avi", ".mkv")):
                    file_path = os.path.join(root, file)
                    subprocess.run(["start", file_path], shell=True)
                    speak(f"Playing {video_name} from your video library.")
                    return
        speak("I couldn't find that video in your library.")
    except Exception as e:
        logging.error(f"Error playing offline video: {e}")
        speak(f"An error occurred while trying to play the video offline. {str(e)}")

def stop_video():
    try:
        mixer.music.stop()
        speak("Video playback stopped.")
    except Exception as e:
        logging.error(f"Error stopping video: {e}")
        speak(f"An error occurred while stopping the video. {str(e)}")

def play_video(command):
    if "online" in command:
        video_name = command.replace("play", "").replace("online", "").strip()
        if video_name:
            speak(f"Searching for {video_name} online.")
            play_online_video(video_name)
        else:
            speak("Please specify the video name.")
    elif "offline" in command:
        video_name = command.replace("play", "").replace("offline", "").strip()
        if video_name:
            speak(f"Searching for {video_name} in your video library.")
            play_offline_video(video_name)
        else:
            speak("Please specify the video name.")
    elif "stop" in command:
        stop_video()
    else:
        speak("Please specify whether to play the video online or offline.")

def check_online_status():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False

def tell_online_status():
    if check_online_status():
        message = "Yes, you are online."
    else:
        message = "No, you are offline."
    speak(message)
    return message

def get_time():
    return datetime.datetime.now().strftime("%I:%M %p")

def get_date():
    today = datetime.date.today()
    return today.strftime("%A, %B %d, %Y")

def tell_joke():
    joke = pyjokes.get_joke()
    return joke

def get_weather(city):
    api_key = config.WEATHER_API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url).json()
    if response.get('main'):
        temp = response['main']['temp']
        weather_desc = response['weather'][0]['description']
        return f"The current temperature in {city} is {temp}°C with {weather_desc}."
    return "Weather information is unavailable."

def get_location():
    try:
        location = geocoder.ip('me')
        if location.ok:
            city = location.city
            state = location.state
            country = location.country
            full_address = location.address
            location_message = f"You are currently in {city}, {state}, {country}. The detailed address is {full_address}."
            speak(location_message)
            print(location_message)
        else:
            error_message = "Sorry, I couldn't retrieve your location."
            speak(error_message)
            print(error_message)
    except Exception as e:
        error_message = f"An error occurred while getting the location: {e}"
        speak(error_message)
        print(error_message)

def perform_web_browsing(command):
    command = command.lower().strip()

    # Handle 'open' command
    if command.startswith("open"):
        website = command.replace("open", "").strip()
        if "youtube" in website:
            speak("Opening YouTube")
            webbrowser.open("https://www.youtube.com")
        elif "google" in website:
            speak("Opening Google")
            webbrowser.open("https://www.google.com")
        elif "." in website:
            speak(f"Opening {website}")
            webbrowser.open(f"https://{website}")
        else:
            speak(f"Opening {website}")
            webbrowser.open(f"https://www.{website}.com")

    elif command.startswith(("search", "what is", "who is", "tell about")):
        query = command
        for phrase in ["search", "what is", "who is", "tell about", "for"]:
            query = query.replace(phrase, "")
        query = query.strip()
        if not query:
            speak("Please tell me what to search for.")
            return

        speak(f"Searching for {query}...")
        url = f"https://api.duckduckgo.com/?q={query.replace(' ', '+')}&format=json&no_html=1&skip_disambig=1"

        try:
            response = requests.get(url)
            data = response.json()

            if data.get("AbstractText"):
                speak(data["AbstractText"])
            elif data.get("RelatedTopics"):
                first_topic = data["RelatedTopics"][0]
                if isinstance(first_topic, dict) and "Text" in first_topic:
                    speak(first_topic["Text"])
                else:
                    speak(f"I found something, but I can't read it out.")
            else:
                speak("Sorry, I couldn't find a clear answer, but I've opened the search in your browser.")
                webbrowser.open(f"https://google.com/?q={query.replace(' ', '+')}")
        except Exception as e:
            speak(f"An error occurred: {str(e)}")

    else:
        speak("Sorry, I didn't understand the browsing command.")

def shutdown():
    system_platform = platform.system().lower()
    if system_platform == "windows":
        subprocess.run(["shutdown", "/s", "/f", "/t", "0"])
    elif system_platform == "linux" or system_platform == "darwin":
        subprocess.run(["shutdown", "-h", "now"])

def restart():
    system_platform = platform.system().lower()
    if system_platform == "windows":
        subprocess.run(["shutdown", "/r", "/f", "/t", "0"])
    elif system_platform == "linux" or system_platform == "darwin":
        subprocess.run(["reboot"])

def sleep_system():
    system_platform = platform.system().lower()
    if system_platform == "windows":
        subprocess.run(["powercfg", "/hibernate", "off"])
        subprocess.run(["rundll32", "powrprof.dll,SetSuspendState", "Sleep"])
    elif system_platform == "linux" or system_platform == "darwin":
        subprocess.run(["systemctl", "suspend"])

def perform_system_action(command):
    if "shutdown" in command:
        speak("Shutting down the system.")
        shutdown()
    elif "restart" in command:
        speak("Restarting the system.")
        restart()
    elif "sleep" in command or "hibernate" in command:
        speak("Putting the system to sleep.")
        sleep_system()
    else:
        speak("I don't recognize that command for system management.")

def assistant_loop():
    speak("Hello! I am Luna, your virtual assistant. How can I help you today?")
    while True:
        command = listen()
        if "who are you" in command:
            speak('''Hi, I’m Luna, A Virtual Assistant! 
            I’m here to make life easier, 
            whether it’s managing tasks, answering your questions, 
            or just sharing a laugh. 
            With my AI-powered capabilities, 
            I can help you stay organized, provide weather updates, 
            Best of all, I’m always ready to assist.''')
        elif "time" in command:
            speak(f"The current time is {get_time()}.")
        elif "date" in command:
            speak(f"Today's date is {get_date()}.")    
        elif "joke" in command:
            speak(f"Here's a joke for you: {tell_joke()}.")      
        elif "weather" in command:
            speak("Which city would you like the weather for?")
            city = listen()
            speak(get_weather(city))
        elif "location" in command:
            speak("Let me find your current location")
            location = get_location()
            speak(location)
        elif "am i online" in command:
            tell_online_status()
        elif "play" in command:
            play_video(command)
        elif "shutdown" in command or "restart" in command or "sleep" in command:
            perform_system_action(command)   
        elif "open" in command or "search" in command or "who is" in command or "what is" in command or "tell about" in command:
            perform_web_browsing(command)            
        elif "exit" in command or "bye" in command or "back" in command or "goodbye" in command:
            speak("Goodbye!")
            break
        else:
            speak("I am not sure how to help with that yet.")

def start_assistant():
    assistant_thread = threading.Thread(target=assistant_loop)
    assistant_thread.daemon = True
    assistant_thread.start()

if __name__ == "__main__":
    start_assistant()
    window.mainloop()
    
