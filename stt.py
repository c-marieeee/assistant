import speech_recognition as sr
import pyaudio
import requests
import json
import pyttsx3

def listen_and_transcribe():
    # Initialize recognizer and text-to-speech engine
    recognizer = sr.Recognizer()
    engine = pyttsx3.init()
    
    print("Listening for trigger word 'SkyNet'...")
    
    while True:
        # Use microphone as source
        with sr.Microphone() as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source)
            
            try:
                # Listen for speech
                audio = recognizer.listen(source, timeout=5)
                
                # Convert speech to text using Google's speech recognition
                text = recognizer.recognize_google(audio)
                print("Heard:", text)
                
                # Check for trigger word
                if "skynet" in text.lower():
                    print("Trigger word detected!")
                    engine.say("How can I help you?")
                    engine.runAndWait()
                    
                    # Listen for the actual question
                    print("Listening for your question...")
                    audio = recognizer.listen(source, timeout=5)
                    question = recognizer.recognize_google(audio)
                    print("Your question:", question)
                    
                    # Send question to Ollama API
                    url = "http://localhost:11434/api/generate"
                    payload = {
                        "model": "llama3.2:latest",
                        "prompt": question
                    }
                    
                    response = requests.post(url, json=payload)
                    print("Debug - Status Code:", response.status_code)
                    
                    if response.status_code == 200:
                        # Handle streaming response by concatenating all responses
                        full_response = ""
                        for line in response.text.strip().split('\n'):
                            if line:
                                try:
                                    parsed = json.loads(line)
                                    if 'response' in parsed:
                                        full_response += parsed['response']
                                except json.JSONDecodeError as e:
                                    print("Debug - JSON parse error:", e)
                                    continue
                        
                        print("AI Response:", full_response)
                        # Speak the AI response
                        engine.say(full_response)
                        engine.runAndWait()

                        # Listen for follow-up response for 10 seconds
                        print("Listening for follow-up response...")
                        try:
                            audio = recognizer.listen(source, timeout=10)
                            follow_up = recognizer.recognize_google(audio)
                            print("Follow-up:", follow_up)
                            
                            # Send follow-up to Ollama API
                            payload["prompt"] = follow_up
                            response = requests.post(url, json=payload)
                            
                            if response.status_code == 200:
                                full_response = ""
                                for line in response.text.strip().split('\n'):
                                    if line:
                                        try:
                                            parsed = json.loads(line)
                                            if 'response' in parsed:
                                                full_response += parsed['response']
                                        except json.JSONDecodeError as e:
                                            print("Debug - JSON parse error:", e)
                                            continue
                                
                                print("AI Response:", full_response)
                                engine.say(full_response)
                                engine.runAndWait()
                        except sr.WaitTimeoutError:
                            print("No follow-up detected. Shutting down conversation.")
                            engine.say("SkyNet shutting down...")
                            engine.runAndWait()
                    else:
                        error_msg = f"Error getting response from Ollama API. Status code: {response.status_code}"
                        print(error_msg)
                        print(f"Response content: {response.text}")
                        engine.say(error_msg)
                        engine.runAndWait()
                
            except sr.WaitTimeoutError as e:
                print("No speech detected within timeout period. Continuing to listen...")
                continue
            except sr.UnknownValueError as e:
                print("Could not understand audio. Continuing to listen...")
                continue
            except sr.RequestError as e:
                error_msg = "Could not request results from Google Speech Recognition service."
                print(error_msg)
                print(f"Error details: {str(e)}")
                print(f"Error type: {type(e).__name__}")
                engine.say(error_msg)
                engine.runAndWait()
            except requests.RequestException as e:
                error_msg = f"Error connecting to Ollama API. Error details: {str(e)}"
                print(error_msg)
                print(f"Error type: {type(e).__name__}")
                engine.say(error_msg)
                engine.runAndWait()
                if hasattr(e, 'response'):
                    print(f"Response status code: {e.response.status_code}")
                    print(f"Response content: {e.response.text}")

if __name__ == "__main__":
    listen_and_transcribe()
