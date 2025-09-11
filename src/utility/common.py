import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import random, requests, json, re, os, sys, time, html, random



def setup_driver(instance_id: int, headless: bool) -> webdriver.Chrome:
    """Configure and return a Chrome WebDriver."""
    options = Options()
    if headless:
        options.add_argument("--headless")        
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Assign a unique remote debugging port
    options.add_argument(f"--remote-debugging-port={9222 + instance_id}")
    
    # Assign a unique user-data-dir
    user_data_dir = tempfile.mkdtemp(prefix=f"chrome-profile-{instance_id}-")
    options.add_argument(f"user-data-dir={user_data_dir}")
    
    driver = webdriver.Chrome(service=Service(), options=options)
    return driver

def connect_with_running_browser(instance_id: int) -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless")
    options.debugger_address = f"127.0.0.1:{9222 + instance_id}"   # connect to the port from Script A
    driver = webdriver.Chrome(options=options)
    return driver

def navigate_to_url(*,driver, url: str) -> None:
    """Navigate to a specified URL."""
    driver.get(url)
    
def open_url_in_new_tab(driver, url):
    driver.execute_script(f"window.open('{url}', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])
    tabs = driver.window_handles
    new_tab = tabs[-1]
    return new_tab

def get_random_amount(amounts: list) -> int:
    """
    Returns a random amount from the provided list.
    
    :param amounts: List of integers/floats to choose from
    :return: Randomly selected amount
    """
    if not amounts:
        raise ValueError("Amount list cannot be empty")
    return random.choice(amounts)

def extract_upi_ids(html_content):
    # Regular expression pattern for extracting UPI IDs
    upi_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z.-]+\b'
    
    # Find all UPI IDs using regex
    upi_ids = re.findall(upi_pattern, html_content)
    
    # Check if any UPI IDs were found
    if upi_ids:
        # Join UPI IDs with two line breaks in between
        return upi_ids
        # return '\n\n'.join(upi_ids)
    else:
        return False
    
# GOOGLE_WEBHOOK="https://chat.googleapis.com/v1/spaces/AAQAOLGKt3w/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=Q4ClsEVZ8sDXtIl80UJt_r-QlV9_zFnWz439H7Ou6os"
GOOGLE_WEBHOOK="https://chat.googleapis.com/v1/spaces/AAQA1CVd6gs/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=3-uHzQfaLRqMQd5HIRYbM1HtZCMKCkXI5Ih0kO5a7Gg"


UNIQUE_GOOGLE_WEBHOOK_DAFABET='https://chat.googleapis.com/v1/spaces/AAQA519Psto/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=dRBJmt0X5Z0q8NZIsgFC58-BUgMxjUkFibFKSHH-Rjc'

DATABASE_URL="postgresql://neondb_owner:npg_KgOtCI7aSx8b@ep-old-cell-adtisbyf-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def send_message(message, webhook_url="https://chat.googleapis.com/v1/spaces/AAQAOLGKt3w/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=Q4ClsEVZ8sDXtIl80UJt_r-QlV9_zFnWz439H7Ou6os"):
    """
    Sends a message to Google Chat using the provided webhook URL.
    
    Args:
        webhook_url (str): The Google Chat webhook URL.
        message (str): The message to be sent.
    """
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    payload = {
        "text": message
    }

    try:
        response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            print("Message sent successfully.")
        else:
            print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while sending message: {e}")
        
        
def has_valid_upi_suffix(upi_id: str) -> bool:
    suffixes = [
        "@ybl", "@axl", "@ibl", "@airtel", "@freecharge", "@pty", "@ptyes",
        "@gmail.com", "@ikwik", "@oksbi", "@ptaxis", "@pthdfc", "@okaxis",
        "@okhdfcbank"
    ]
    
    return any(upi_id.endswith(suffix) for suffix in suffixes)

def get_invalid_upi_ids(upi_ids: list[str]) -> list[str]:
    suffixes = [
        "@ybl", "@axl", "@ibl", "@airtel", "@freecharge", "@pty", "@ptyes",
        "@gmail.com", "@ikwik", "@oksbi", "@ptaxis", "@pthdfc", "@okaxis",
        "@okhdfcbank"
    ]
    
    invalid_upis = [
        upi for upi in upi_ids
        if not any(upi.endswith(suffix) for suffix in suffixes)
    ]
    
    return invalid_upis