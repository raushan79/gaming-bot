from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import random, requests, json, re, os, sys, time, html
from selenium import webdriver

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.utility.logger import get_logger
from src.utility.db import PostgresDB
from src.utility.common import send_message, UNIQUE_GOOGLE_WEBHOOK_DAFABET, has_valid_upi_suffix, get_invalid_upi_ids,DATABASE_URL

db = PostgresDB(url=DATABASE_URL)


logger = get_logger(__name__, "dafabet.log")

"""
_summary_
Game Variable configuration
"""
HOME_PAGE_URL = "https://www.dfbocai.net/in/"
USER_NAME = 'Ratankr'
PASSWORD='Patna12345'
AMOUNT_LIST = [1000, 5000, 10000, 15000, 50000, 80000]

def start():
    logger.info("Dafabet bot started for get upi id")
    driver = connect_with_running_browser()
    new_url_tab = open_url_in_new_tab(driver, HOME_PAGE_URL)
    time.sleep(2)
    deposite_url = extract_deposite_amount_url(driver)
    go_to_url(driver, deposite_url)
    # click_on_deposit(driver)
    # go to home url
    logger.info(f"Deposite url: {deposite_url}")
    # deposite_url_tab = open_url_in_new_tab(driver, deposite_url)
    click_payment_option(driver)
    time.sleep(5)
    logger.info("Clicked on payment option")
    # select_option = select_random_cashier_option(driver)
    # logger.info(f"select sports option: {select_option}")
    pay_amount = get_random_amount(AMOUNT_LIST)
    enter_amount(driver, pay_amount)
    logger.info(f"Enter amount: {pay_amount}")
    click_submit(driver)
    logger.info("Clicked on submit button")
    time.sleep(10)
    logger.info("Waiting for page to load...")
    html_content = driver.page_source
    time.sleep(40)
    upi_id = extract_upi_ids(html_content)
    unique_upi_id = list(set(upi_id)) if upi_id else []
    logger.info(f"Extracted UPI IDs: {upi_id}")
    
    # execute_query
    if unique_upi_id:
        # check upi id if exist then get send with counter
        check_existing_upi_query = f""" SELECT bot_name, upi_id, counter FROM upi_id_table WHERE upi_id= %s """
        check_existing_upi_query_params = (unique_upi_id,)
        existing_upi_id_details = db.execute(check_existing_upi_query, check_existing_upi_query_params)
        print(f"existing_upi_id_details : {existing_upi_id_details}")
        if not existing_upi_id_details:
        # send upi id and insert in db
            insert_upi_id_query = f""" INSERT INTO upi_id_table (bot_name, upi_id, counter) VALUES (%s, %s, %s) """
            insert_upi_id_query_params = ('dafabet',unique_upi_id, 1)
            db.execute(insert_upi_id_query, insert_upi_id_query_params)
        
            upi_ids = get_invalid_upi_ids(unique_upi_id)
            if upi_ids:
                message = f"{', '.join(upi_ids)}"
                send_message(message, UNIQUE_GOOGLE_WEBHOOK_DAFABET)
            else:
                logger.info("No invalid UPI IDs found.")
    else:
        logger.info("No UPI IDs found on the page.")
    # close the tab
    logger.info("Process completed. Closing the browser.")
    driver.close()
    
def click_submit(driver, timeout: int = 20):
    """
    Clicks the submit button with selector #edit-submit.
    
    :param driver: Selenium WebDriver instance
    :param timeout: Max wait time in seconds
    """
    selector = "#edit-submit"
    
    # Wait until button is clickable
    button = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
    )
    
    button.click()
    return True
def enter_amount(driver, amount, timeout: int = 120):
    """
    Enters the given amount into the #edit-amount input field.
    
    :param driver: Selenium WebDriver instance
    :param amount: Value to enter (int, float, or str)
    :param timeout: Max wait time in seconds
    """
    selector = "#edit-amount"
    
    # Wait until field is visible
    field = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
    )
    
    # Clear existing text
    field.clear()
    
    # Type in the amount
    field.send_keys(str(amount))
    
    return True
def click_payment_option(driver, timeout: int = 120):
    selector = ("body > div.wrapper.desktop.menubile-content > main > div.container > "
                "div.block.block-cashier > div.payment-option > "
                "div:nth-child(1) > div > div > a > div.group-payment-option-logo")
    
    # wait for element to be clickable
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
    )
    element.click()

def go_to_url(driver,url):
    logger.info(f"Navigating to URL: {url}")
    driver.get(url)
    
def open_url_in_new_tab(driver, url):
    driver.execute_script(f"window.open('{url}', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])
    logger.info(f"Opened new tab with URL: {url}")
    # Get all tabs
    tabs = driver.window_handles

    # The new tab is the last one in the list
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

def select_random_cashier_option(driver, timeout: int = 120):
    """
    Opens the cashier dropdown and selects a random option.
    """
    # 1. Click on the dropdown to expand it
    dropdown_selector = "#cashier-form-item > div > div.form-item.form-type-select.form-item-product > span > div > div.selectedTxt"
    dropdown = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, dropdown_selector))
    )
    dropdown.click()

    # 2. Wait for dropdown options to appear
    options_selector = "div.form-item.form-type-select.form-item-product ul li"
    options = WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, options_selector))
    )

    # 3. Pick a random option
    option = random.choice(options)

    # 4. Click the option
    option.click()

    return option.text  # return selected option text

    
def connect_with_running_browser():
    options = Options()
    options.add_argument("--headless")
    options.debugger_address = "127.0.0.1:9222"   # connect to the port from Script A
    driver = webdriver.Chrome(options=options)
    return driver
    

def extract_deposite_amount_url(driver, timeout: int = 120) -> str:
    selector = ("#frosmo_message_id_51 > header > div > div > div.account-section.text-right.toggable.no-product-balance > div.player-options.hide-text.mb-25 > ul > li.cashier-tooltip.tooltip.last > div > ul > li:nth-child(1) > a")
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        href = el.get_attribute("href")
        return html.unescape(href) if href else ""
    except TimeoutException:
        return "Not found url"
    
def click_on_deposit(driver, timeout: int = 120) -> str:
    wait = WebDriverWait(driver, timeout)

    # Hover over "Cashier"
    cashier = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.cashier-label")))
    ActionChains(driver).move_to_element(cashier).perform()

    # Wait for Deposit link (first <li>) to be clickable and click it
    deposit = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, ".tooltip-content ul li:nth-child(1) a")
    ))
    deposit.click()

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
    




if __name__ == "__main__":
    while True:
        try:
            start()
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            time.sleep(10)  # wait before retrying
            start()