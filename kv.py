from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from dotenv import load_dotenv
import threading
import os
from tkinter import *
from tkinter import messagebox
from tkinter import scrolledtext

# --- Constants ---
BASE_URL = "https://www.karaoke-version.com"
LOGIN_URL = f"{BASE_URL}/my/login.html"
CUSTOM_TRACK_URL_TEMPLATE = f"{BASE_URL}/custombackingtrack/{{artist}}/{{song}}.html"

# --- GUI Setup ---
def create_gui():
    """Creates and configures the Tkinter GUI."""
    window = Tk()
    window.title("KV Downloader")
    window.wm_attributes("-topmost", 1)  # Keep window on top
    window.geometry('600x280')

    # Configure grid
    window.columnconfigure(0, weight=1)
    window.columnconfigure(1, weight=3)

    Label(window, text='Karaoke Version Song URL:', anchor=E).grid(column=0, row=0, sticky=E, padx=5, pady=2)
    txt_url = Entry(window, width=60)
    txt_url.grid(column=1, row=0, sticky=W, padx=5, pady=2)

    # Status box
    Label(window, text="Status:", anchor=W).grid(column=0, row=1, columnspan=2, sticky=W, padx=5, pady=(10, 0))
    status_box = scrolledtext.ScrolledText(window, height=8, state='disabled')
    status_box.grid(column=0, row=2, columnspan=2, sticky="nsew", padx=5, pady=2)
    window.rowconfigure(2, weight=1)  # Allow status box to expand vertically

    # Button calls download_tracks with values from entry fields
    fetch_btn = Button(window, text="Fetch Tracks")
    fetch_btn.grid(column=1, row=3, pady=10, sticky='w', padx=5)

    cancel_btn = Button(window, text="Cancel", state="disabled")
    cancel_btn.grid(column=1, row=3, pady=10, sticky='e', padx=5)

    # Create a shared event to signal cancellation from the GUI to the worker thread
    cancel_event = threading.Event()

    # The button command will now start the download in a separate thread
    fetch_btn.config(command=lambda: start_download_thread(
        txt_url.get(), status_box, fetch_btn, cancel_btn, cancel_event))
    cancel_btn.config(command=cancel_event.set)

    return window

def log_message(status_box, message):
    """Prints a message to the console and inserts it into the GUI status box."""
    print(message)
    status_box.configure(state='normal')
    status_box.insert(END, message + "\n")
    status_box.configure(state='disabled')
    status_box.see(END) # Auto-scroll to the bottom
    status_box.update_idletasks()

def start_download_thread(url, status_box, fetch_button, cancel_button, cancel_event):
    """Disables the button and starts the download process in a new thread to keep the GUI responsive."""
    fetch_button.config(state="disabled") # Disable fetch button
    cancel_button.config(state="normal")  # Enable cancel button
    cancel_event.clear() # Ensure the cancel flag is reset at the start

    thread = threading.Thread(
        target=download_tracks,
        args=(url, status_box, fetch_button, cancel_button, cancel_event)
    )
    thread.start()

# --- Core Logic ---
def download_tracks(url, status_box, fetch_button, cancel_button, cancel_event):
    """Logs into Karaoke-Version and downloads all solo tracks for a song."""
    total_tracks = 0 # Initialize to 0
    load_dotenv()
    user = os.getenv('KV_USER')
    password = os.getenv('KV_PASSWORD')

    if not user or not password:
        messagebox.showerror("Configuration Error", "KV_USER and/or KV_PASSWORD not found in your .env file.\n\nPlease ensure your .env file contains:\nKV_USER=your_username\nKV_PASSWORD=your_password")
        return

    # Use URL field if Artist is BLANK, otherwise construct the URL
    song_url = url.strip()

    if not song_url:
        messagebox.showwarning("Input Missing", "Please provide an Artist/Song or a direct URL.")
        return

    # Initialize webdriver
    driver = None
    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        wait = WebDriverWait(driver, 20) # Explicit wait object

        # --- Login ---
        log_message(status_box, 'Logging in...')
        if cancel_event.is_set(): raise Exception("Operation cancelled by user.")
        driver.get(LOGIN_URL)

        # Handle cookie consent banner if it appears
        try:
            cookie_wait = WebDriverWait(driver, 5) # Shorter wait for an optional element
            agree_button = cookie_wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))
            log_message(status_box, "Accepting cookies...")
            agree_button.click()
        except Exception:
            log_message(status_box, "Cookie banner not found or already accepted, continuing...")

        if cancel_event.is_set(): raise Exception("Operation cancelled by user.")
        wait.until(EC.visibility_of_element_located((By.ID, "frm_login"))).send_keys(user)
        driver.find_element(By.ID, "frm_password").send_keys(password)
        driver.find_element(By.ID, "sbm").click()

        # CRITICAL: Wait for the post-login page to load before navigating away.
        # This confirms the session is established.
        # We wait for the URL to change from the login page, which is a robust way to confirm navigation.
        wait.until(EC.url_changes(LOGIN_URL))
        if cancel_event.is_set(): raise Exception("Operation cancelled by user.")
        log_message(status_box, "Login successful.")

        # --- Song Page ---
        log_message(status_box, f'Loading Song URL: {song_url}')
        driver.get(song_url)

        # Verify login success by checking for the "My account" link on the song page.
        # Login verification has been disabled as it was causing issues.

        # Wait for track list to be visible
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'track__solo')))

        # --- Page Interaction ---
        # Ensure 'intro precount' checkbox is checked
        precount_checkbox = driver.find_element(By.ID, 'precount')
        if not precount_checkbox.is_selected():
            log_message(status_box, 'Enabling precount...')
            precount_checkbox.click()

        # Find all solo track buttons
        solo_buttons = driver.find_elements(By.CLASS_NAME, 'track__solo')
        total_tracks = len(solo_buttons)
        log_message(status_box, f'Number of Tracks Found: {total_tracks}')

        # --- Download Loop ---
        # We loop by index to avoid StaleElementReferenceException.
        # The DOM can change after a download, making the original list of buttons stale.
        # By re-finding the buttons on each iteration, we ensure we have a fresh reference.
        for index in range(total_tracks):
            # Mute all other tracks by clicking the current track's solo button
            if cancel_event.is_set(): break # Check for cancellation before each download
            solo_button = driver.find_elements(By.CLASS_NAME, 'track__solo')[index]
            solo_button.click()

            # Wait for the download button to become enabled (i.e., the 'disabled' class is gone)
            download_button = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.download:not(.disabled)")))

            # Use a JavaScript click to prevent ElementClickInterceptedException from sticky footers/headers
            driver.execute_script("arguments[0].click();", download_button)
            log_message(status_box, f'Downloading Track: [{index + 1} of {total_tracks}]')

            # Wait for the download modal and then close it
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'begin-download__manual-download')))
            driver.find_element(By.CSS_SELECTOR, ".js-modal-close").click()
            # Wait for modal to disappear
            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'begin-download__manual-download')))

        if cancel_event.is_set():
            log_message(status_box, "\nDownload process cancelled by user.")
        else:
            log_message(status_box, '\nALL DONE!')
            messagebox.showinfo("Success", f"All {total_tracks} tracks have been downloaded.")

    except Exception as e:
        log_message(status_box, f"An error occurred: {e}")
        if "cancelled by user" not in str(e):
            messagebox.showerror("Error", f"An error occurred:\n{e}")
    finally:
        if driver:
            log_message(status_box, "Closing browser.")
            driver.quit()
        # Re-enable the button when the process is finished or fails
        fetch_button.config(state="normal")
        cancel_button.config(state="disabled")

if __name__ == "__main__":
    gui = create_gui()
    gui.mainloop()