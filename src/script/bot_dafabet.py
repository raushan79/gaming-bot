"""
_summary_
Dafabet sports gamming bot 
web link : https://www.dfbocai.net/in/
home url :  https://www.dfbocai.net/in/

"""
import sys, os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.utility.logger import get_logger


logger = get_logger(__name__, "dafabet.log")

"""
_summary_
Game Variable configuration
"""
HOME_PAGE_URL = "https://www.dfbocai.net/in/"
USER_NAME = 'Ratankr'
PASSWORD='Patna12345'



def start():
    logger.info("Dafabet bot started")
    driver = setup_driver()
    
    try:
        login(driver, USER_NAME, PASSWORD)
        time.sleep(5)

    finally:
        input("Press Enter to close the browser...")
        driver.quit()
        
def setup_driver() -> webdriver.Chrome:
    """Configure and return a Chrome WebDriver."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--remote-debugging-port=9222")   # enable debugging
    options.add_argument("user-data-dir=/tmp/chrome-profile")  # keep session/cookies
    driver = webdriver.Chrome(service=Service(), options=options)
    return driver


def login(driver: webdriver.Chrome, username: str, password: str) -> None:
    """Perform login on the site."""
    logger.info("Navigating to homepage...")
    driver.get(HOME_PAGE_URL)
    time.sleep(2)

    logger.info("Filling login form...")
    # Locate input by ID and type the username
    username_input = driver.find_element(By.ID, "LoginForm_username")
    username_input.clear()  # optional: clears any pre-filled text
    username_input.send_keys(USER_NAME)

    # Locate password field by ID and type the password
    password_input = driver.find_element(By.ID, "LoginForm_password")
    password_input.clear()  # optional: clear if anything is pre-filled
    password_input.send_keys(PASSWORD)

    login_button = driver.find_element(By.ID, "LoginForm_submit")
    login_button.click()

    time.sleep(3)
    logger.info("Login completed")
    
def extract_urls_from_driver(driver) -> dict[str, str]:
    """
    Extract link text and URLs from the cashier menu using Selenium driver.
    
    Args:
        driver (webdriver): Selenium WebDriver instance (already on the page).

    Returns:
        dict[str, str]: Dictionary mapping link text -> href.
    """
    links = driver.find_elements(By.CSS_SELECTOR, "li.cashier-tooltip a[data-popup='true']")
    return {link.text.strip(): link.get_attribute("href") for link in links}

if __name__ == "__main__":
    start()
