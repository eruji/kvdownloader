from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from dotenv import load_dotenv
import os
from tkinter import *

# create GUI
window = Tk()
window.title("KV Downloader")
window.geometry('450x200')

lbl_a = Label(window, anchor=E, width=30, text="Artist, eg. john-mayer:")
lbl_s = Label(window, anchor=E, width=30, text="Song, eg. born-and-raised:")
lbl_a.grid(column=0, row=2)
lbl_s.grid(column=0, row=4)

txt_a = Entry(window,width=30)
txt_s = Entry(window,width=30)
txt_a.grid(column=1, row=2)
txt_s.grid(column=1, row=4)


# function called by gui click
def download_tracks(a, s):
    load_dotenv()
    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    artist = str(a)  # os.getenv('ARTIST')
    song = str(s)  # os.getenv('SONG')
    songURL = "https://www.karaoke-version.com/custombackingtrack/"+artist+"/"+song+".html"

    if len(artist) > 1:
        print('.env set so using that...')
        songURL = "https://www.karaoke-version.com/custombackingtrack/"+artist+"/"+song+".html"
    else:
        print('####Enter Song URL: (right click to paste)####')
        songURL = input()

    # create webdriver and open page #selenium v4
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver = webdriver.Chrome(ChromeDriverManager().install())

    # driver.maximize_window()
    print('Logging in...')
    driver.get("https://www.karaoke-version.com/my/login.html")

    # login
    driver.find_element(By.CSS_SELECTOR, "#frm_login").send_keys(user)
    driver.find_element(By.CSS_SELECTOR, "#frm_password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "#sbm").click()

    # wait for screen to load
    driver.implicitly_wait(4)

    # load song url
    print('Loading Song URL...')
    driver.get(songURL)
    # driver.implicitly_wait(30)
    time.sleep(15)

    # intro precount checkbox
    precount = driver.find_element(By.ID, 'precount')  # .click()
    print('Precount is Selected:', precount.is_selected())
    if precount.is_selected() == False:
        precount.click()

    # Find Solo elements
    Solo = driver.find_elements(By.CLASS_NAME, 'track__solo')

    # Number of Tracks
    TotalTracks = len(Solo)
    print('Number of Tracks Found:', TotalTracks)

    # loop
    for (x, i) in enumerate(Solo, start=1):
        print('Solo is Enabled', i.is_enabled())
        if i.is_selected() == False:
            i.click()
        driver.find_element(By.CLASS_NAME, 'download').click()
        print('Downloading Track: [', x, 'of', TotalTracks, ']')
        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'begin-download__manual-download')))
        driver.find_element(By.CSS_SELECTOR, ".js-modal-close").click()

    # enable solo on track2 so loop can start at 1
    Solo[1].click
    time.sleep(2)

    # loop
    for (x, i) in enumerate(Solo, start=1):
        i.click()
        driver.find_element(By.CLASS_NAME, 'download').click()
        print('Downloading Track: [', x, 'of', TotalTracks, ']')
        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'begin-download__manual-download')))
        driver.find_element(By.CSS_SELECTOR, ".js-modal-close").click()

        print("you've made it to the end")
        time.sleep(60)


# button creation and function call
btn = Button(window, text="Fetch Tracks", command=lambda: download_tracks(txt_a.get(), txt_s.get()))
btn.grid(column=1, row=6)

window.mainloop()

