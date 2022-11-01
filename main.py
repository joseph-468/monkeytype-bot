from pynput.keyboard import *
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController
from pytesseract import pytesseract
import pyautogui
from PIL import Image
import time
import threading
import cv2
import json

# Config
with open("config.json") as file:
    config = json.load(file)

if config["RESET_CONFIG"] is True:
    with open("config_default.json") as file:
        default_settings = json.load(file)
        with open("config.json", "w") as file:
            json.dump(default_settings, file, indent=2)

with open("config.json") as file:
    config = json.load(file)

coords = config["screenshotSize"]
left, top, bottom, right = coords["left"], coords["top"], coords["bottom"], coords["right"]
pytesseract.tesseract_cmd = config["tesseractPath"]
path = config["screenshotPath"]
correct_chars = config["correctChars"]
typing_settings = config["typingSettings"]
typing_speed = (typing_settings["WPM"] - 1) * 1000
file.close()

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
        config["screenshotSize"]["left"], config["screenshotSize"]["top"] = mouse.position
        with open("config.json", "w") as file:
            json.dump(config, file, indent=2)
        file.close()

    elif key == Key.page_down:
        print(f"Bottom right: (X: {mouse.position[0]}, Y: {mouse.position[1]})")
        right, bottom = mouse.position
        config["screenshotSize"]["right"], config["screenshotSize"]["bottom"] = mouse.position
        with open("config.json", "w") as file:
            json.dump(config, file, indent=2)
        file.close()


def get_text_from_image():
    # Take screenshot
    pyautogui.screenshot(path)
    im = Image.open(path)
    im = im.crop((left, top, right, bottom))
    im.save(path)
    img = cv2.imread("screenshot.png")
    # Clean text
    sentence = pytesseract.image_to_string(img).lower()
    linebreaks = "".join(i for i in sentence if i in correct_chars)
    sentence = " ".join("".join(i for i in sentence.replace("\n", " ") if i in correct_chars).split())
    print(sentence)
    return sentence, linebreaks


def type_sentence():
    global running
    sentence, linebreaks = get_text_from_image()
    # Type text
    delay = 3000 / typing_speed * 2
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
