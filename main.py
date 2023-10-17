import openai
import speech_recognition as sr
import os
from google.cloud import texttospeech
import pygame
import json


# Needed installs: pip install openai speechrecognition google-cloud-texttospeech pygame 

# sudo apt-get install portaudio19-dev python-pyaudio python3-pyaudio 

 

# If you get errors connected to GLIBCXX_3.4.29 run:  
# sudo apt-get install libgtk-4-dev 
# GTK_PATH=/usr/lib/x86_64-linux-gnu/gtk-4.0 


# Run without ALSA errors
# python3 main.py 2>> error_log.txt

# Initialize the recognizer
recognizer = sr.Recognizer()

# Path for google text to speach api key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"

# Setting up OpenAI API key
with open('openai_api.json', 'r') as file:
    config = json.load(file)
    openai.api_key = config['OPENAI_API_KEY']

def recognize_speech_from_mic():
    print("Hello! You can start speaking now. Say 'hello hi' to start the conversation.")
    with sr.Microphone() as source:
        while True:
            print("Listening for 'hello hi' trigger...")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            try:
                speech_text = recognizer.recognize_google(audio)
                print(f"Heard: {speech_text}")
                if speech_text.lower().startswith("hello hi"):
                    print("Trigger detected! Entering conversation mode.")
                    # Speaking the welcome message
                    speak_text_google("Hello, please ask me your question.")
                    conversation_mode(source)
            except sr.UnknownValueError:
                # Google Speech Recognition couldn't understand the audio
                pass

def conversation_mode(source):
    conversation_history = ""  # Initialize an empty conversation history for this session
    while True:
        print("Listening for your question...")
        audio = recognizer.listen(source)
        try:
            user_input = recognizer.recognize_google(audio)
            print(f"You said: {user_input}")

            if user_input.lower() in ["goodbye", "stop"]:
                speak_text_google("Goodbye!")
                print("Goodbye!")
                return  # Exiting the conversation mode

            # Add user's input to the conversation history
            conversation_history += f"User: {user_input}\n"

            # Interact with OpenAI API
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=conversation_history + "AI:",
                max_tokens=150,
                n=1,
                stop=None,
                temperature=0.5,
            )

            gpt_response = response.choices[0].text.strip()
            print("Response:", gpt_response)

            # Add AI's response to the conversation history
            conversation_history += f"AI: {gpt_response}\n"

            # Log the conversation to a file
            log_filename = "conversation_log.txt"  # This can be moved outside of the function if you don't want a new file for each session
            log_conversation_to_file(log_filename, user_input, gpt_response)

            # Speak the response using Google Cloud's Text-to-Speech
            speak_text_google(gpt_response)

        except sr.UnknownValueError:
            print("Sorry, I didn't catch that. Please try again or say 'goodbye' to exit.")


def speak_text_google(text):
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=input_text,
        voice=voice,
        audio_config=audio_config
    )

    filename = "output.mp3"
    with open(filename, "wb") as out:
        out.write(response.audio_content)

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


def log_conversation_to_file(log_filename, user_input, gpt_response):
    with open(log_filename, "a", encoding="utf-8") as f:
        f.write(f"User: {user_input}\n")
        f.write(f"AI: {gpt_response}\n\n")



if __name__ == '__main__':
    recognize_speech_from_mic()

