from datetime import datetime
from datetime import timedelta
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
import json

with open('./eversports.json') as eversports:
    data = json.load(eversports)
    EVERSPORTS_MAIL = data["email"]
    EVERSPORTS_PW = data["password"]

RECONNECT_ATTEMPTS = 3
DEBUG_MODE = False

SPORTCENTER_KAUTZ_SQUASH_URL = "https://www.eversports.de/widget/w/qc7bpq?sport=squash"

AMS_MARISA_WEEKDAY_FROM = 1
AMS_MARISA_WEEKDAY_TO = 4
AMS_MARISA_TIME_FROM = 19
AMS_MARISA_TIME_TO = 20 + 1 #range excludes last number

NO_BOOK_DATES = ["2023-02-16", "2023-02-17"] #, "2023-02-20", "2023-02-21"]

class TimeSlotMinimum60Minutes(Exception):
    pass

class GuestsOnlyAllowedToHaveTwoOpenHours(Exception):
    pass

def book_squash():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(options=chrome_options)

    attempts = 0
    while attempts < RECONNECT_ATTEMPTS:
        try:
            driver.get(SPORTCENTER_KAUTZ_SQUASH_URL)
            break
        except WebDriverException:
            attempts += 1
            print("ERROR: Internet connection lost.")

    print("------------------------------------------")
    print("------------------------------------------")

    title = driver.title
    print(title)
    assert title == "Online-Buchung"

    driver.implicitly_wait(5)

    booking_info = driver.find_element(By.ID, "booking-info")

    new_week_available = True
    while new_week_available:
        if searchBookingTable(driver):
            break
        
        next_week_button = driver.find_element(By.XPATH, "//button[@id='next-week']")
        if next_week_button.is_enabled():
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@id='next-week']"))).click()
            sleep(1)
        else:
            new_week_available = False

    print("INFO: Search terminated.")

    driver.quit()

def searchBookingTable(driver):
    booking_table = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//table[@class='date-table table table-bordered']")))
    time_slots = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.XPATH, "//td[@class='combined-slot es-tooltip'][@data-start]"))
    )

    last_time_slot_is_suitable = False
    for time_slot in time_slots: #195
        current_time_slot_is_free = time_slot_free(time_slot)

        if current_time_slot_is_free and last_time_slot_is_suitable:
            try:
                book_time_slot(driver, last_time_slot)
                return True
            except TimeSlotMinimum60Minutes:
                print("ERROR: Hier muss eine Buchung mindestens 60 Minuten dauern.")
                return True
            except GuestsOnlyAllowedToHaveTwoOpenHours:
                print("ERROR: Gäste dieser Sportstätte dürfen nur 2 offene Stunden haben.")
                return True
        
        last_time_slot = time_slot
        last_time_slot_is_suitable = time_slot_suitable(time_slot)

    time_slot_start = last_time_slot.get_attribute("data-startdate") + " " + last_time_slot.get_attribute("data-start")
    time_slot_start_dt = datetime.strptime(time_slot_start, "%Y-%m-%d %H%M")
    
    print("NOT FOUND: No free courts found until: " + time_slot_start_dt.strftime("%Y-%m-%d %H:%M"))
    return False

def time_slot_free(time_slot):
    if not time_slot.get_attribute('innerHTML') == "Frei":
         return False

    return True

def time_slot_suitable(time_slot):
    if not time_slot_free(time_slot):
        return False

    time_slot_start = time_slot.get_attribute("data-startdate") + " " + time_slot.get_attribute("data-start")
    time_slot_start_dt = datetime.strptime(time_slot_start, "%Y-%m-%d %H%M")
    if not check_if_time_is_good(1, 5, time_slot_start_dt):
        return False

    print("Suitable slot at: " + time_slot_start_dt.strftime("%Y-%m-%d %H:%M"))

    return True

def book_time_slot(driver, time_slot):
    time_slot.click()
    accept_cookies(driver, time_slot)
    login(driver)
    checkForErrorAfterLogin(driver)
    addVoucher(driver)
    choosePaymentMethod(driver)

    sleep(0.5)
    time_slot_start = time_slot.get_attribute("data-startdate") + " " + time_slot.get_attribute("data-start")
    time_slot_start_dt = datetime.strptime(time_slot_start, "%Y-%m-%d %H%M")
    print("INFO: Slot " + time_slot_start_dt.strftime("%Y-%m-%d %H:%M") + " booked.")

def accept_cookies(driver, time_slot):
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='accept-all-cookies']"))).click()

def login(driver):
    driver.find_element(By.ID, ":Rptiv:").send_keys(EVERSPORTS_MAIL)
    driver.find_element(By.ID, ":R19tiv:").send_keys(EVERSPORTS_PW)
    driver.find_element(By.XPATH, "//button[@data-testid='login']").submit()

def checkForErrorAfterLogin(driver):
    try:
        driver.find_element(By.XPATH, "//p[normalize-space()='Hier muss eine Buchung mindestens 60 Minuten dauern.']")
        raise TimeSlotMinimum60Minutes
    except NoSuchElementException:
        return False

def addVoucher(driver):
    driver.find_element(By.XPATH, "//button[@data-testid='voucher-show-input']").click()
    driver.find_element(By.NAME, "voucher").send_keys("clever")
    driver.find_element(By.XPATH, "//button[normalize-space()='Gutschein einlösen']").click()

def choosePaymentMethod(driver):
    driver.find_element(By.XPATH, "//button[@data-testid='continue'][normalize-space()='Zahlungsart wählen']").click()
    driver.implicitly_wait(5)
    checkForErrorAfterChosingPaymentMethod(driver)
    driver.find_element(By.XPATH, "//p[normalize-space()='Zahlung mit Paypal']").click()
    if not DEBUG_MODE:
        driver.find_element(By.XPATH, "//button[@data-testid='continue'][normalize-space()='Jetzt zahlen']").click()

def checkForErrorAfterChosingPaymentMethod(driver):
    try:
        driver.find_element(By.XPATH, "//p[normalize-space()='Gäste dieser Sportstätte dürfen nur 2 offene Stunden haben. Du kannst daher erst wieder buchen, wenn eine deiner zukünftigen Stunden gespielt oder storniert wurde.']")
        raise GuestsOnlyAllowedToHaveTwoOpenHours
    except NoSuchElementException:
        return False

def check_if_time_is_good(typeOfPersonGroup, disableNextXDays, dt):
    #disable next 3 days for test
    today = datetime.now()
    today += timedelta(days=disableNextXDays)
    if dt <= today:
        return False

    #check no book dates
    for no_book_date in NO_BOOK_DATES:
        no_book_date = datetime.strptime(no_book_date, "%Y-%m-%d").date()
        if dt.date() == no_book_date:
            return False

    # Squash Ams + Marisa
    if typeOfPersonGroup == 1:
        if not dt.isoweekday() in range(AMS_MARISA_WEEKDAY_FROM, AMS_MARISA_WEEKDAY_TO):
            return False

        if not dt.hour in range(AMS_MARISA_TIME_FROM, AMS_MARISA_TIME_TO):
            return False
    
        return True
    #Padel Adri + Carlos + Marmol + Issam + Pablo
    elif typeOfPersonGroup == 2:
        if not dt.isoweekday() in range(1, 5):
            return False

        if not dt.hour in range(19, 22):
            return False
    
        return True
    else:
        return False

book_squash()