import cv2
import pyttsx3
import speech_recognition as sr
import mediapipe as mp
import os

tts_engine = pyttsx3.init()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

sign_dict = {
    'hello': 'sign_images/hello.png',
    'thank': 'sign_images/thank.png',
    'please': 'sign_images/please.png',
    'goodbye': 'sign_images/goodbye.png',
    'yes': 'sign_images/yes.png',
    'no': 'sign_images/no.png',
    'help': 'sign_images/help.png',
    'sorry': 'sign_images/sorry.png',
    'love': 'sign_images/love.png',
    'friend': 'sign_images/friend.png',
}

def set_tts_language(language_code):
    voices = tts_engine.getProperty('voices')
    for voice in voices:
        if language_code in voice.languages:
            tts_engine.setProperty('voice', voice.id)
            break

def text_to_speech(text, language_code='en'):
    set_tts_language(language_code)
    tts_engine.say(text)
    tts_engine.runAndWait()

def text_to_sign(text):
    words = text.lower().split()
    for word in words:
        img_path = sign_dict.get(word)
        if img_path and os.path.exists(img_path):
            img = cv2.imread(img_path)
            if img is not None:
                cv2.imshow("Sign Language", img)
                cv2.waitKey(1000)  
            else:
                print(f"Image for '{word}' not found.")
        else:
            print(f"Sign for '{word}' not available.")
    cv2.destroyAllWindows()

def voice_to_text(language_code='en-IN'):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for voice command...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language=language_code)
            print(f"Recognized text: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand the audio.")
        except sr.RequestError:
            print("Request to Google Speech API failed.")
    return ""

def recognize_hand_gesture():
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                
                if abs(thumb_tip.x - index_tip.x) < 0.05 and abs(thumb_tip.y - index_tip.y) < 0.05:
                    text_to_sign("thank")  
                    text_to_speech("Thank you")  
                

        cv2.imshow("Hand Gesture Recognition", frame)
        if cv2.waitKey(5) & 0xFF == 27:  
            break
    cap.release()
    cv2.destroyAllWindows()

def main():
    print("Choose an option:")
    print("1. Voice command to Text and Sign Language")
    print("2. Real-time Hand Gesture Recognition")
    print("3. Text to Speech")

    choice = input("Enter choice (1/2/3): ")

    print("Choose a language (en, hi, ta, te, kn, ml, bn): ")
    language = input("Enter language code: ")

    language_mapping = {
        'en': 'en-IN',  # English (India)
        'hi': 'hi-IN',  # Hindi
        'ta': 'ta-IN',  # Tamil
        'te': 'te-IN',  # Telugu
        'kn': 'kn-IN',  # Kannada
        'ml': 'ml-IN',  # Malayalam
        'bn': 'bn-IN',  # Bengali
    }

    language_code = language_mapping.get(language, 'en-IN')

    if choice == '1':
        while True:
            text = voice_to_text(language_code=language_code)
            if text.lower() == "exit":
                break
            elif text:
                text_to_sign(text)

    elif choice == '2':
        recognize_hand_gesture()

    elif choice == '3':
        text = input("Enter text to convert to speech: ")
        text_to_speech(text, language_code=language_code)

    else:
        print("Invalid choice. Please choose 1, 2, or 3.")

if __name__ == "__main__":
    main()
