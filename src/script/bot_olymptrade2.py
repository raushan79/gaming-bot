from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import random, requests, json, re, os, sys, time, html, random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.utility.logger import get_logger
from src.utility.db import PostgresDB


logger = get_logger(__name__, "olymptrade.log")

from config  import OLYMPTRADE_INSTANCE_ID, OLYMPTRADE_GOOGLE_WEBHOOK
from src.utility.common import setup_driver, connect_with_running_browser, navigate_to_url, open_url_in_new_tab,get_random_amount, extract_upi_ids, send_message, UNIQUE_GOOGLE_WEBHOOK_DAFABET, has_valid_upi_suffix, get_invalid_upi_ids,DATABASE_URL
db = PostgresDB(url=DATABASE_URL)

HOME_PAGE_URL = "https://olymptrade.com/platform"
# USER_NAME = 'Ratankr'
USER_EMAIL = 'mrkr852131@gmail.com'
USER_PASSWORD='Patna123'
AMOUNT_LIST = [700, 1500, 2000, 7000, 15000, 25000, 5000, 10000, 15000, 50000]
bot_name = "olymptrade"




def start():
    logger.info("Olymptrade bot started for get upi id")
    driver = connect_with_running_browser(instance_id=OLYMPTRADE_INSTANCE_ID)
    open_url_in_new_tab(driver, HOME_PAGE_URL)
    click_on_payment(driver)
    amount = get_random_amount(AMOUNT_LIST)
    enter_amount(driver, amount)
    # click on confirm button 
    confirm_btn = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable((By.XPATH, "//span[@data-trans='confirm']"))
    )
    confirm_btn.click()
    # click on next button
    next_btn = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable((By.XPATH, "//span[@data-trans='next']"))
    )
    next_btn.click()
    
    # click on next confirm
    confirm_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[@data-trans='confirm']"))
    )
    confirm_btn.click()
    
    # switch to opened tabl window
    # Wait for a new window/tab to appear
    WebDriverWait(driver, 120).until(lambda d: len(d.window_handles) > 1)

    # Switch to the newest tab
    time.sleep(3)
    driver.switch_to.window(driver.window_handles[-1])

    print("✅ Switched to new tab:", driver.current_url)
    
    # enter payment details and proceed
    enter_payment_details_and_proceed(driver)
    

    logger.info("Waiting for page to load...")
    time.sleep(30)
    html_content = driver.page_source
    upi_id = extract_upi_ids(html_content)
    logger.info(f"Extracted upi_id : {upi_id}")
    unique_upi_id = upi_id[0] if upi_id else []
    logger.info(f"unique_upi_id UPI IDs: {unique_upi_id}")
    
    # execute_query
    if unique_upi_id:
        check_existing_upi_query = f""" SELECT bot_name, upi_id, counter FROM upi_id_table WHERE upi_id= %s """
        check_existing_upi_query_params = (unique_upi_id,)
        existing_upi_id_details = db.execute(check_existing_upi_query, check_existing_upi_query_params)
        print(f"existing_upi_id_details : {existing_upi_id_details}")
        message = unique_upi_id
        if not existing_upi_id_details:
        # send upi id and insert in db
            insert_upi_id_query = f""" INSERT INTO upi_id_table (bot_name, upi_id, counter) VALUES (%s, %s, %s) """
            insert_upi_id_query_params = ('olymptrade',unique_upi_id, 1)
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
    # driver.close()
    # close all tab and first tab open 
    # Keep the first tab, close all others
    main_tab = driver.window_handles[0]

    for handle in driver.window_handles:
        if handle != main_tab:
            driver.switch_to.window(handle)
            driver.close()


def insert_upi_id_with_counter(bot_name: str, unique_upi_id: str, db_path: str = "prisma/database.db") -> int:
    """
    Check if a UPI ID already exists for a bot_name, 
    get the count, and insert a new record with counter = count + 1.
    Returns the inserted counter value.
    """
    # Step 1: check existing count
    check_exist_count_query = """
        SELECT COUNT(*) 
        FROM upi_id_table 
        WHERE bot_name = ? AND upi_id = ?
    """
    result = execute_query(db_path=db_path, query=check_exist_count_query, params=(bot_name, unique_upi_id))
    count_value = result[0][0] if result else 0

    # Step 2: insert with counter = count + 1
    insert_upi_id_query = """
        INSERT INTO upi_id_table (bot_name, upi_id, counter) 
        VALUES (?, ?, ?)
    """
    params = (bot_name, unique_upi_id, count_value + 1)
    execute_query(db_path=db_path, query=insert_upi_id_query, params=params)

    return count_value + 1

def get_and_update_screenshot_counter(bot_name: str, db_path: str = "prisma/database.db") -> int:
    """
    Fetch the current screenshot_counter for a given bot_name,
    increment it by 1, update it in the database, and return the new value.
    """
    # Step 1: Get existing counter
    get_counter_query = """
        SELECT screenshot_counter 
        FROM upi_screenshot_counter 
        WHERE bot_name = ? 
        LIMIT 1;
    """
    result = execute_query(db_path=db_path, query=get_counter_query, params=(bot_name,))
    counter = result[0][0] if result else 0

    # Step 2: Increment
    counter += 1

    # Step 3: Update counter in DB
    update_counter_query = """
        UPDATE upi_screenshot_counter 
        SET screenshot_counter = ? 
        WHERE bot_name = ?;
    """
    execute_query(db_path=db_path, query=update_counter_query, params=(counter, bot_name))

    return counter
    

def click_on_payment(driver):
    payment_button = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "span[data-trans='payments']"))
    )
    payment_button.click()
    logger.info("Payment button clicked successfully!")
    deposit_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[@data-trans='cabinet_tab_recharge']"))
    )
    deposit_btn.click()
    logger.info("Deposit button clicked successfully!")
    
def enter_amount(driver, amount):
    amount_box = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-test='textBox'] span[data-test='value-selected_amount']"))
    )
    amount_box.click()
    input_field = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='amount']"))
    )
    input_field.send_keys(Keys.COMMAND + "a") 
    input_field.send_keys(Keys.BACKSPACE) 
    input_field.send_keys(str(amount))   
    
def enter_payment_details_and_proceed(driver):
    # enter name 
    # Wait until the input is ready
    first_name_input = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable((By.NAME, "first_name"))
    )

    # Clear any existing text and type the name
    first_name_input.clear()
    first_name_input.send_keys("John")
    last_name_input = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable((By.NAME, "last_name"))
    )

    last_name_input.clear()
    last_name_input.send_keys("Doe")   # replace with your variable
    phone_input = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable((By.NAME, "phone"))
    )

    phone_input.clear()
    phone_input.send_keys("7542021197") 
    vpa_input = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable((By.NAME, "vpa"))
    )

    vpa_input.clear()
    vpa_input.send_keys("7542021197@ybl")
    
    proceed_btn = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable((By.XPATH, "//span[text()='Proceed to payment']"))
    )
    proceed_btn.click()
    
    time.sleep(5)
    proceed_btn = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable((By.XPATH, "//span[normalize-space(text())='Proceed to payment']"))
    )
    proceed_btn.click()
    time.sleep(5)



    
if __name__ == "__main__":
    while True:
        try:
            time.sleep(2)
            start()
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            time.sleep(10)  # wait before retrying
            start()