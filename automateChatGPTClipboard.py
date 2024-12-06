import time
import threading
import pyperclip
from selenium_profiles.webdriver import Chrome
from selenium_profiles.profiles import profiles
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

profile = profiles.Windows()
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.binary_location = (
    "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
)
driver = Chrome(
    profile,
    options=options,
    uc_driver=False,
)

driver.get("https://chatgpt.com")
n = 3
RESPONSE_TIMEOUT = 60


def get_prompt_response(prompt):
    global n
    textarea = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "prompt-textarea"))
    )
    textarea.send_keys(prompt)
    button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "button[data-testid='send-button']")
        )
    )
    button.click()
    print(f"\rWaiting for response...           ", end="")
    try:
        response = WebDriverWait(driver, RESPONSE_TIMEOUT).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, f"article[data-testid='conversation-turn-{n}']")
            )
        )
        print(f"\rWaiting for response to end... ", end="")
        while(len(response.text.split("\n")) <= 1):
            time.sleep(1)
        while driver.find_elements(By.CSS_SELECTOR, "div.result-streaming"):
            time.sleep(0.25)
    except TimeoutException:
        n = n + 2
        return ""
    print(f"\rProcessing response...            ", end="")

    response = response.text
    if "You’re giving feedback on a new version of ChatGPT." in response:
        response = response.replace(
            "You’re giving feedback on a new version of ChatGPT.", ""
        )
        response = response.replace(
            "Which response do you prefer? Responses may take a moment to load.", ""
        )
        response = response.replace("Response 1", "")
        response = response.replace("Response 2", "")
        response = response.replace("Response 3", "")
        response = response.replace("I prefer this response", "")
    n = n + 2
    response = response.split("\n")
    del response[0]
    response = "{0}".format(".".join(response))
    return f"{response:<33}"


count = 0


class ClipboardWatcher(threading.Thread):
    def __init__(self, predicate, callback):
        super(ClipboardWatcher, self).__init__()
        self._predicate = predicate
        self._callback = callback
        self._stopping = False

    def run(self):
        recent_value = pyperclip.paste()
        while not self._stopping:
            tmp_value = pyperclip.paste()
            if tmp_value != recent_value:
                recent_value = tmp_value
                if self._predicate(recent_value):
                    self._callback(recent_value)

    def stop(self):
        self._stopping = True


def on_change(text):
    print(f"\rProcessing prompt...", end="")
    response = get_prompt_response(text)
    if pyperclip.is_available():
        pyperclip.copy(response)
        print(f"\rWARNING: {response}", end="")

    else:
        print(f"\r{response}", end="")


def process_text(text: str):
    global count
    count = count + 1
    return count % 2 != 0


def main():
    watcher = ClipboardWatcher(process_text, on_change)
    watcher.start()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            watcher.stop()
            break


if __name__ == "__main__":
    main()