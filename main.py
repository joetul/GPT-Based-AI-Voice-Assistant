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


def recognize_speech_from_mic():
    with sr.Microphone() as source:
        print("Say something...")
        audio = recognizer.listen(source)
        speech_text = recognizer.recognize_google(audio)
        return speech_text


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


def main():
    with open('openai_api.json', 'r') as file:
        config = json.load(file)
        openai.api_key = config['OPENAI_API_KEY']

    print("Hello! You can start speaking now. Say 'goodbye' to end the conversation.")

    conversation_history = ""
    log_filename = "conversation_log.txt"

    while True:
        user_input = recognize_speech_from_mic()

        if user_input:
            print(f"You said: {user_input}")

            if user_input.lower() in ["goodbye", "stop"]:
                speak_text_google("Goodbye!")
                print("Goodbye!")
                break

            # Add user's input to the conversation history
            conversation_history += f"User: {user_input}\n"

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
            log_conversation_to_file(log_filename, user_input, gpt_response)

            # Speak the response using Google Cloud's Text-to-Speech
            speak_text_google(gpt_response)
        else:
            print("Sorry, I didn't catch that. Please try again or say 'goodbye' to end the conversation.")


if __name__ == '__main__':
    main()
