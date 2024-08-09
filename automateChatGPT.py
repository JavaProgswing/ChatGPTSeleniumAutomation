from selenium_profiles.webdriver import Chrome
from selenium_profiles.profiles import profiles
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import argparse

parser = argparse.ArgumentParser(
    description="A script to automate ChatGPT using selenium hidden with selenium profiles."
)
parser.add_argument(
    "-showBrowser", action="store_true", help="Show browser if this flag is passed"
)

args = parser.parse_args()
show_browser = args.showBrowser
profile = profiles.Windows()
options = webdriver.ChromeOptions()
if not show_browser:
    options.add_argument("--headless=new")
options.binary_location = (
    "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
)
# Change the browser binary location to the path of your browser

driver = Chrome(
    profile,
    options=options,
    uc_driver=False,
)


class TextStabilized:
    def __init__(self, locator, timeout, interval=1):
        self.locator = locator
        self.timeout = timeout
        self.interval = interval

    def __call__(self, driver):
        end_time = time.time() + self.timeout
        last_text = None
        while time.time() < end_time:
            element = driver.find_element(*self.locator)
            current_text = element.text
            if last_text == current_text:
                return current_text
            last_text = current_text
            time.sleep(self.interval)
        return False


driver.get("https://chatgpt.com")
n = 3
RESPONSE_TIMEOUT = 60  # Timeout for waiting for ChatGPT's response


def wait_until_loaded():
    WebDriverWait(driver, -1).until(
        EC.presence_of_element_located((By.ID, "prompt-textarea"))
    )


def print_prompt_response(prompt):
    print(
        "\rWaiting for ChatGPT's response...        ",
        end="",
    )
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
    try:
        response = WebDriverWait(driver, RESPONSE_TIMEOUT).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, f"div[data-testid='conversation-turn-{n}']")
            )
        )
        response = WebDriverWait(driver, RESPONSE_TIMEOUT + 5).until(
            TextStabilized(
                (By.CSS_SELECTOR, f"div[data-testid='conversation-turn-{n}']"),
                RESPONSE_TIMEOUT,
            )
        )
    except TimeoutException:
        n = n + 2
        print("\rTimeout: ChatGPT did not respond in time!")
        return
    if type(response) != str:
        print("\rAn unexpected error occurred, try again!")
        return
    print(f"\r{response:<33}")
    n = n + 2


wait_until_loaded()
print("Enter the prompt: ", end="")
prompt = input()
print_prompt_response(prompt)
while True:
    print("Do you want to send a prompt? (y/n): ", end="")
    input_str = input()
    if input_str != "y" and input_str != "n":
        print("Invalid input. Please enter 'y' or 'n'!")
        continue

    if input_str == "y":
        print("Enter the prompt: ", end="")
        prompt = input()
        print_prompt_response(prompt)
    else:
        print("Exiting...")
        break
