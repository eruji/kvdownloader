# selenium 3
# from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
#selenium 4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by   import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from dotenv import load_dotenv
import os


#load_dotenv()
def getTracks(u,p,a,s):
    user = str(u) #s.getenv('USER')
    password = str(p) #os.getenv('PASSWORD')
    artist = str(a) #os.getenv('ARTIST')
    song = str(s) #os.getenv('SONG')
    songURL = "https://www.karaoke-version.com/custombackingtrack/"+artist+"/"+song+".html"

    # create webdriver and open page #selenium v4
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver = webdriver.Chrome(ChromeDriverManager().install())

    #driver.maximize_window()
    print('Logging in...')
    driver.get("https://www.karaoke-version.com/my/login.html")

    # login
    driver.find_element(By.CSS_SELECTOR,"#frm_login").send_keys(user)
    driver.find_element(By.CSS_SELECTOR,"#frm_password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR,"#sbm").click()

    # wait for screen to load
    driver.implicitly_wait(4)

    # load song url
    print('Loading Song URL...')
    driver.get(songURL)
    # driver.implicitly_wait(30)
    time.sleep(15)

    # intro precount checkbox
    precount = driver.find_element(By.ID,'precount')#.click()
    print('Precount is Selected:',precount.is_selected())
    if precount.is_selected() == False:
        precount.click()

    # Find Solo elements
    Solo = driver.find_elements(By.CLASS_NAME,'track__solo')

    # Number of Tracks
    TotalTracks = len(Solo)
    print('Number of Tracks Found:',TotalTracks)

    #loop
    for (x,i) in enumerate(Solo,start=1):
        print('Solo is Enabled',i.is_enabled())
        if i.is_selected() == False:
            i.click()
        driver.find_element(By.CLASS_NAME,'download').click()
        print('Downloading Track: [',x,'of',TotalTracks,']')
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME, 'begin-download__manual-download')))
        driver.find_element(By.CSS_SELECTOR,".js-modal-close").click()

    print("you've made it to the end")
    time.sleep(60)