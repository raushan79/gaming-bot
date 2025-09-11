"""
_summary_
Dafabet sports gamming bot 
web link : https://olymptrade.com/
home url :  https://www.dfbocai.net/in/

"""
import sys, os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.utility.logger import get_logger
from config  import OLYMPTRADE_INSTANCE_ID
from src.utility.common import setup_driver,navigate_to_url


logger = get_logger(__name__, "dafabet.log")

"""
_summary_
Game Variable configuration
"""
HOME_PAGE_URL = "https://olymptrade.com/platform"
# USER_NAME = 'Ratankr'
USER_EMAIL = 'mrkr852131@gmail.com'
USER_PASSWORD='Patna123'



def start():
    logger.info("Olymptrade bot started")
    driver = setup_driver(OLYMPTRADE_INSTANCE_ID, headless=True)
    
    try:
        navigate_to_url(driver=driver, url=HOME_PAGE_URL)
        login(driver, USER_EMAIL, USER_PASSWORD)
        time.sleep(5)

    finally:
        input("Press Enter to close the browser...")
        driver.quit()

def login(driver: webdriver.Chrome, username: str, password: str) -> None:
    """Perform login on the site."""
    login_button = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 
            "#page-container > div.main > div > div > div > div > div.u4RexuYxHFeV > div > div > button:nth-child(1)")
        )
    )
    login_button.click()
    logger.info("Login button clicked successfully!")
    # Wait until the email input is visible
    email_input = WebDriverWait(driver, 120).until(
        EC.visibility_of_element_located((By.NAME, "email"))
    )

    # Clear any pre-filled value and enter your password
    email_input.clear()
    email_input.send_keys(USER_EMAIL)
    logger.info("Email entered successfully!")
    password_input = WebDriverWait(driver, 120).until(
        EC.visibility_of_element_located((By.NAME, "password"))
    )

    # Clear any pre-filled value and enter your email
    password_input.clear()
    password_input.send_keys(USER_PASSWORD)
    logger.info("Password entered successfully!")
    login_span = WebDriverWait(driver, 120).until(
    EC.element_to_be_clickable((By.XPATH, "//span[text()='Log In']"))
)
    login_span.click()
    logger.info("Login clicked successfully!")

    
    
    
    
if __name__ == "__main__":
    start()