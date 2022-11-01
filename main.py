from pynput.keyboard import *
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController
from pytesseract import pytesseract
import pyautogui
from PIL import Image
import time
import random
import threading
import cv2
import json

# Config
with open("config.json") as file:
    config = json.load(file)
coords = config["screenshotSize"][0]
left, top, bottom, right = coords["left"], coords["top"], coords["bottom"], coords["right"]
pytesseract.tesseract_cmd = config["tesseractPath"]
path = config["screenshotPath"]
correct_chars = config["correctChars"]
typing_settings = config["typingSettings"][0]
typing_speed = (typing_settings["WPM"] - 1) * 1000

# Setup
mouse = MouseController()
keyboard = KeyboardController()
running = False
print("Started Typing Bot.")


def on_press(key):
    global running
    global left, top, bottom, right
    # Close on escape
    if key == Key.esc:
        running = False
        exit()
    elif key == Key.delete:
        # Start/Stop typing
        if not running:
            running = True
            threading.Thread(target=type_sentence).start()
        else:
            running = False
    # Set screenshot size
    elif key == Key.page_up:
        print(f"Top left: (X: {mouse.position[0]}, Y: {mouse.position[1]})")
        left, top = mouse.position
    elif key == Key.page_down:
        print(f"Bottom right: (X: {mouse.position[0]}, Y: {mouse.position[1]})")
        right, bottom = mouse.position


def type_sentence():
    global running
    # Get text from screen
    pyautogui.screenshot(path)
    im = Image.open(path)
    im = im.crop((left, top, right, bottom))
    im.save(path)
    img = cv2.imread("screenshot.png")
    # Clean text
    sentence = pytesseract.image_to_string(img).lower()
    sentence = sentence.replace("-", "")
    sentence = " ".join("".join(i for i in sentence.replace("\n", " ") if i in correct_chars).split())
    print("".join(sentence))
    # Type text
    delay = 3000 / typing_speed * 2
    print(delay)
    for char in sentence:
        if not running:
            break
        time.sleep(delay)
        keyboard.press(char)
        time.sleep(delay)
        keyboard.release(char)
    running = False


with Listener(on_press=on_press) as listener:
    listener.join()
