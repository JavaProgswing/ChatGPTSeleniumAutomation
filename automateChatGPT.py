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

driver.get("https://chatgpt.com")
n = 3
RESPONSE_TIMEOUT = 60  # Timeout for waiting for ChatGPT's response


def wait_until_loaded():
    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.ID, "prompt-textarea"))
        )
    except:
        wait_until_loaded()


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
                (By.CSS_SELECTOR, f"article[data-testid='conversation-turn-{n}']")
            )
        )
        while(len(response.text.split("\n")) <= 1):
            time.sleep(1)
        while (
            driver.find_elements(By.CSS_SELECTOR, "div.result-streaming")
        ):
            time.sleep(0.25)
    except TimeoutException:
        n = n + 2
        print("\rTimeout: ChatGPT did not respond in time!")
        return

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
    response = response.split("\n")
    del response[0]
    response = "{0}".format(".".join(response))
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