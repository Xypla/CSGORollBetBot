import configparser
import math
import os

import time

from selenium.common import TimeoutException

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.options import Options


def login():
    # Click the login button
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '/html/body/cw-root/cw-header/nav/div[2]/div/cw-auth-buttons/div/button'))).click()
    # Find and fill username box
    except TimeoutException as e:
        return
    username_box = WebDriverWait(driver, 60).until(EC.element_to_be_clickable(
        (By.XPATH, '/html/body/div[1]/div[7]/div[2]/div/div[2]/div[2]/div/form[1]/input[4]')))
    username_box.clear()
    username_box.send_keys(USERNAME)
    # Find and fill password box
    pass_box = WebDriverWait(driver, 60).until(EC.element_to_be_clickable(
        (By.XPATH, '/html/body/div[1]/div[7]/div[2]/div/div[2]/div[2]/div/form[1]/input[5]')))
    pass_box.clear()
    pass_box.send_keys(PASS)
    # Click the login button again
    WebDriverWait(driver, 60).until(EC.element_to_be_clickable(
        (By.XPATH, '/html/body/div[1]/div[7]/div[2]/div/div[2]/div[2]/div/form[1]/div[4]/input'))).click()
    # Get authenticator code
    auth_code = input('Please enter your steam guard authenticator code: ')
    # Find and fill auth code box

    auth_box = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div[3]/div/div/div/form/div[3]/div[1]/div/input')))
    auth_box.clear()
    auth_box.send_keys(auth_code)
    # CLik the submit button
    button_container = driver.find_element(By.ID, "login_twofactorauth_buttonset_entercode")
    button_container.find_element(By.XPATH, "*").click()

    # Reset bet amount
    bet_box = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH,
                                                                          '/html/body/cw-root/mat-sidenav-container/mat-sidenav-content/div/cw-roulette/div/div[2]/cw-amount-input/mat-form-field/div/div[1]/div[3]/div[2]/input')))
    bet_box.clear()


def round_two(number):
    return math.ceil(number * 100) / 100


def log_to_file(string, file):
    print(f"Write to file {file}")
    with open(file, "a") as f:
        f.write(string)


def bet():
    counter = driver.find_element(By.XPATH,
                                  "/html/body/cw-root/mat-sidenav-container/mat-sidenav-content/div/cw-roulette/div/div[2]/div[1]/cw-next-roll/div")

    timer = counter.find_elements(By.XPATH, "*")[1]

    history = driver.find_element(By.XPATH,
                                  "/html/body/cw-root/mat-sidenav-container/mat-sidenav-content/div/cw-roulette/div/header/cw-roulette-game-rolls/section/div")

    input_field = driver.find_element(By.XPATH,
                                      "/html/body/cw-root/mat-sidenav-container/mat-sidenav-content/div/cw-roulette/div/div[2]/cw-amount-input/mat-form-field/div/div[1]/div[3]/div[2]/input")

    red_b = driver.find_element(By.XPATH,
                                "/html/body/cw-root/mat-sidenav-container/mat-sidenav-content/div/cw-roulette/div/div[2]/div[2]/section/cw-roulette-bet-button[1]/div/button")
    black_b = driver.find_element(By.XPATH,
                                  "/html/body/cw-root/mat-sidenav-container/mat-sidenav-content/div/cw-roulette/div/div[2]/div[2]/section/cw-roulette-bet-button[3]/div/button")
    green_b = driver.find_element(By.XPATH,
                                  "/html/body/cw-root/mat-sidenav-container/mat-sidenav-content/div/cw-roulette/div/div[2]/div[2]/section/cw-roulette-bet-button[2]/div/button")

    balance = driver.find_element(By.XPATH,
                                  "/html/body/cw-root/cw-header/nav/div[2]/div/section[1]/cw-user-balance/div/cw-pretty-balance/span")

    jackpot = float(driver.find_element(By.XPATH, "/html/body/cw-root/mat-sidenav-container/mat-sidenav-content/div/cw-roulette/div/header/div/cw-roulette-jackpot/div/div/cw-pretty-balance/span").text.replace(",", ""))
    # ### Analyse vars ###
    last_jackpot = jackpot
    highest_count = 0
    # ### Analyse vars ###

    wait_for_jackpot = False

    start_balance = float(balance.text)
    red_counter = 0
    black_counter = 0
    green_count = 0

    last_g_c = 0
    last_r_c = 0
    last_b_c = 0

    global START_BET
    current_green_bet = START_BET
    current_bet = START_BET
    bet_placed = False

    last = None
    profit = 0
    lost_last = False
    last_balance = 0

    profit_counter = 0

    #Debug safety:
    hard_stop = HARD_STOP

    while True:
        if float(balance.text) > last_balance:
            lost_last = False

        if float(timer.get_attribute("innerHTML")) > 2 and not bet_placed:
            h_fields = history.find_elements(By.XPATH, "*")

            if lost_last:
                print("lost last")
                current_bet += START_BET / 2
            elif profit < 0:
                current_bet = START_BET
            else:
                current_bet -= START_BET / 2



            for field in h_fields:
                if "bg-red" in field.get_attribute("class"):
                    if last == "bg-red" or last is None or (last == "bg-green" and black_counter == 0):
                        red_counter += 1
                        last = "bg-red"

                        if red_counter > BET_AFTER:
                            current_bet *= 2.1
                    else:
                        break
                elif "bg-black" in field.get_attribute("class"):
                    if last == "bg-black" or last is None or (last == "bg-green" and red_counter == 0):
                        black_counter += 1
                        last = "bg-black"

                        if black_counter > BET_AFTER:
                            current_bet *= 2.1
                    else:
                        break
                elif "bg-green" in field.get_attribute("class"):
                    if green_count >= 3:
                        green_count = 0
                        last = "bg-green"
                    if last == "bg-green" or last is None:
                        green_count += 1
                        last = "bg-green"
                    current_bet *= 2.1

            print(f"Current red count: {red_counter}")
            print(f"Current black count: {black_counter}")
            print(f"Current green count: {green_count}")

            if black_counter >= STOP_DOUBLE:
                highest_count = black_counter
            elif red_counter >= STOP_DOUBLE:
                highest_count = red_counter

            last_jackpot = check_jackpot(jackpot, last_jackpot)

            if wait_for_jackpot:
                if jackpot < AVERAGE_JACKPOT:
                    print("Waiting for Jackpot")
                    time.sleep(60)
                    continue
                else:
                    print("Do not waiting for Jackpot")
                    wait_for_jackpot = False

            if float(balance.text) < hard_stop:
                current_bet = 0
                if jackpot > AVERAGE_JACKPOT:
                    current_green_bet = 0.5
                else:
                    current_green_bet = 0

            place_bet(black_b, black_counter, current_bet, current_green_bet, green_b, green_count, input_field, red_b, red_counter)


            #Profit calc
            last_balance = float(balance.text)
            profit = last_balance - start_balance

            if (hard_stop + 50) < last_balance:
                hard_stop += 3

            if profit > 0:
                profit_counter += 1
                if profit_counter == 20:
                    start_balance = last_balance
            else:
                profit_counter = 0

            if green_count > 0:
                if profit * 0.02 > START_BET:
                    current_green_bet = profit * 0.02
                else:
                    current_green_bet = START_BET
                    if jackpot > AVERAGE_JACKPOT:
                        current_green_bet *= 2.1

            if highest_count > 0 and red_counter < BET_AFTER > black_counter:
                lost_last = True
                log_to_file(f"{highest_count}\n", "higher_than_stop.txt")
                highest_count = 0

            if last_b_c > black_counter:
                log_to_file(f"{last_b_c}\n", "black_count.txt")
            if last_r_c > red_counter:
                log_to_file(f"{last_r_c}\n", "red_count.txt")
            if last_g_c > green_count:
                log_to_file(f"{last_g_c}\n", "green_count.txt")

            if (START_BET * -50) > profit and jackpot < AVERAGE_JACKPOT and \
                    (BET_AFTER > red_counter or red_counter > STOP_DOUBLE) and \
                    (BET_AFTER > black_counter or black_counter > STOP_DOUBLE):
                wait_for_jackpot = True

            current_bet = START_BET

            last_g_c = green_count
            last_r_c = red_counter
            last_b_c = black_counter

            last = None
            red_counter = 0
            green_count = 0
            black_counter = 0
            bet_placed = True
            print(f"Balance after bet {balance.text}")

            print(f"Profit after bet {profit}")
            print(f"HARD STOP {hard_stop}")

        elif float(timer.get_attribute("innerHTML")) < 1 and bet_placed:
            bet_placed = False
            print("-" * 10)


def check_jackpot(jackpot, last_jackpot):
    if last_jackpot > jackpot:
        log_to_file(f"{last_jackpot}\n", "jackpot.txt")
        last_jackpot = jackpot
    else:
        last_jackpot = jackpot

    return last_jackpot


def place_bet(black_b, black_counter, current_bet, current_green_bet, green_b, green_count, input_field, red_b, red_counter):
    global GREEN_COUNT_TOTAL
    if green_count >= 1:
        GREEN_COUNT_TOTAL += 1
        if GREEN_COUNT_TOTAL > 5:
            input_field.clear()
            input_field.send_keys(round_two(current_green_bet))
            print(f"Bet on green {round_two(current_green_bet)}")
            green_b.click()

    if BET_AFTER <= red_counter < STOP_DOUBLE:
        print(f"Bet on black {round_two(current_bet)}")
        input_field.clear()
        input_field.send_keys(round_two(current_bet))
        black_b.click()

    if BET_AFTER <= black_counter < STOP_DOUBLE:
        print(f"Bet on red {round_two(current_bet)}")
        input_field.clear()
        input_field.send_keys(round_two(current_bet))
        red_b.click()


if __name__ == '__main__':

    config = configparser.ConfigParser()
    if os.path.isfile("./botconfig.ini"):
        config.read("./botconfig.ini")

        USERNAME = config.get('STEAM', 'USER')
        PASS = config.get('STEAM', 'PASSWORD')
        START_BET = config.get("ADVANCED", "START_BET")
        BET_AFTER = config.get("ADVANCED", "BET_AFTER")
        STOP_DOUBLE = BET_AFTER + config.get("ADVANCED", "STOP_DOUBLE")
        AVERAGE_JACKPOT = config.get("ADVANCED", "AVERAGE_JACKPOT")
        HARD_STOP = config.get("ADVANCED", "HARD_STOP")
        GREEN_COUNT_TOTAL = 0
    else:
        config.add_section("STEAM")
        config.set('STEAM', 'USER', "Example_User")
        config.set('STEAM', 'PASSWORD', "123SUPERSAFE")
        config.add_section("ADVANCED")
        config.set("ADVANCED", "START_BET", "0.1")
        config.set("ADVANCED", "BET_AFTER", "2")
        config.set("ADVANCED", "STOP_DOUBLE", "4")
        config.set("ADVANCED", "AVERAGE_JACKPOT", "12000")
        config.set("ADVANCED", "HARD_STOP", "50")

        with open("./botconfig.ini", "w") as configfile:
            config.write(configfile)

        print("Missing config. Example has been created")
        exit(1)

    service = Service('./chromedriver.exe')
    service.start()
    co = Options()
    co.add_argument(f"user-data-dir={os.path.abspath('./Data')}")
    driver = webdriver.Chrome(service=service, options=co)
    driver.set_window_position(2000, 0)
    driver.maximize_window()
    driver.get('https://www.csgoroll.com/en/roll')
    time.sleep(1)

    try:
        # driver.get_screenshot_as_file("headless-chrome.png")
        login()
        time.sleep(1)
        bet()
    finally:
        driver.quit()
