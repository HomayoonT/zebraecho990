import time
import random
import json
import sys
import os
import threading
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set timeout duration (in seconds)
TIMEOUT = 330 * 60 # 330 minutes
START_TIME = time.time()
COOKIE_FILE = "youtube_cookies.json"
CHROME_PROFILE_PATH = os.path.abspath("chrome_profile")
PLAYLIST_URL_FILE = "playlist_url.txt"

UBLOCK_EXTENSION_PATH = "AdBlock"  # Path to UBlock Origin extension

# Setup Chrome with Selenium and ChromeOptions
def get_driver():
    is_new_profile = not os.path.exists(CHROME_PROFILE_PATH)

    if is_new_profile:
        print("🆕 New Chrome profile created.")
        os.makedirs(CHROME_PROFILE_PATH)  # Create profile directory if it doesn't exist
    else:
        print("✅ Chrome profile exists")
    
    driver = Driver(uc=True, headless=False, incognito=False, user_data_dir=CHROME_PROFILE_PATH)

    if is_new_profile:
        print("✅ Attempting to load cookies...")
        load_cookies(driver)

    return driver

def wait_for_page_load(driver, timeout=30):
    """
    Waits for the page to completely load by checking the document.readyState.
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        print("✅ Page loaded completely.")
    except Exception as e:
        print(f"❌ Page load timed out: {e}")

def exit_script():
    if time.time() - START_TIME > TIMEOUT:
        print("❌ Timeout reached. Exiting...")
        sys.exit(0)

def human_like_delay(min_time=1, max_time=3):
    time.sleep(random.uniform(min_time, max_time))

def scroll_like_human(driver):
    for _ in range(random.randint(3, 7)):
        driver.execute_script("window.scrollBy(0, arguments[0]);", random.randint(100, 300))
        human_like_delay(1, 2)

def type_like_human(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))


def human_like_mouse_move(driver, element):
    # Get element's location and size
    element_location = element.location
    element_size = element.size
    element_center_x = element_location['x'] + element_size['width'] / 2
    element_center_y = element_location['y'] + element_size['height'] / 2

    # Get the browser window size
    window_size = driver.get_window_size()
    max_x = window_size["width"] - 1
    max_y = window_size["height"] - 1

    # Ensure the random start position is within bounds
    start_x = min(max(0, random.randint(element_location['x'] - 100, element_location['x'] + element_size['width'] + 100)), max_x)
    start_y = min(max(0, random.randint(element_location['y'] - 100, element_location['y'] + element_size['height'] + 100)), max_y)

    # Move mouse to an initial valid position (top-left of the element)
    ActionChains(driver).move_to_element_with_offset(element, 0, 0).perform()
    time.sleep(random.uniform(0.3, 0.5))

    # Move mouse in small steps toward the center
    current_x, current_y = start_x, start_y
    steps = random.randint(5, 15)
    for _ in range(steps):
        move_x = random.randint(-10, 10)
        move_y = random.randint(-10, 10)

        # Ensure movement is within bounds
        new_x = min(max(0, current_x + move_x), max_x)
        new_y = min(max(0, current_y + move_y), max_y)

        ActionChains(driver).move_by_offset(new_x - current_x, new_y - current_y).perform()
        current_x, current_y = new_x, new_y
        time.sleep(random.uniform(0.05, 0.15))

    # Move directly to element center
    ActionChains(driver).move_to_element(element).perform()
    time.sleep(random.uniform(0.3, 0.5))

    # Click the element
    ActionChains(driver).click().perform()

def move_mouse_randomly(driver):
    """Moves the mouse slightly in a random direction within the video area."""
    try:
        video_element = driver.find_element(By.TAG_NAME, "video")
        action = ActionChains(driver)

        # Get video element position and size
        video_location = video_element.location
        video_size = video_element.size

        # Generate a random offset within the video area
        offset_x = random.randint(10, video_size['width'] - 10)
        offset_y = random.randint(10, video_size['height'] - 10)

        # Move the mouse
        action.move_to_element_with_offset(video_element, offset_x, offset_y).perform()
        time.sleep(random.uniform(0.5, 1.5))
        
    except Exception as e:
        print(f"⚠️ Error moving mouse: {e}")

def pause_video_naturally(driver):
    """Pauses the video for a random duration before resuming."""
    try:
        video_element = driver.find_element(By.TAG_NAME, "video")
        
        # Pause the video
        driver.execute_script("arguments[0].pause();", video_element)
        print("⏸️ Video paused.")

        # Wait for a random time as if the user got distracted
        time.sleep(random.uniform(3, 8))  

        # Resume the video
        driver.execute_script("arguments[0].play();", video_element)
        print("▶️ Video resumed.")
        
    except Exception as e:
        print(f"⚠️ Error pausing video: {e}")

def adjust_volume_randomly(driver):
    """Adjusts the video volume up or down slightly in a natural way."""
    try:
        video_element = driver.find_element(By.TAG_NAME, "video")
        
        # Get current volume (0.0 to 1.0)
        current_volume = driver.execute_script("return arguments[0].volume", video_element)
        
        # Change volume by a small random amount
        volume_change = random.uniform(-0.2, 0.2)
        new_volume = max(0, min(1, current_volume + volume_change))  # Keep within 0-1 range
        
        # Set new volume
        driver.execute_script(f"arguments[0].volume = {new_volume};", video_element)
        print(f"🔊 Volume adjusted to: {new_volume:.2f}")
        
    except Exception as e:
        print(f"⚠️ Error adjusting volume: {e}")

def close_adblock_tab(driver):
    original_window = driver.current_window_handle
    all_windows = driver.window_handles
    for window in all_windows:
        driver.switch_to.window(window)
        if "AdBlock is now installed!" in driver.title:
            print("❌ Found 'AdBlock is now installed!' tab. Closing it...")
            driver.close()
            break
    driver.switch_to.window(original_window)

def read_urls_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            video_urls = [line.strip() for line in file if line.strip()]
        return video_urls
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
        sys.exit(1)

def load_cookies(driver):
   
    try:
        # with open(COOKIE_FILE, "r") as file:
        #     cookies = json.load(file)
        cookies = json.loads(os.environ.get('COOKIES'))

        driver.uc_open("https://www.youtube.com")  # Ensure correct domain is loaded before adding cookies
        wait_for_page_load(driver)
        
        valid_domain = ".youtube.com"

        for cookie in cookies:
            if "domain" in cookie and valid_domain not in cookie["domain"]:
                print(f"Skipping cookie {cookie['name']} due to domain mismatch.")
                continue  # Skip invalid domain cookies
            
            if "sameSite" not in cookie or cookie["sameSite"] not in ["Strict", "Lax", "None"]:
                cookie["sameSite"] = "Lax"
            
            if "expiry" not in cookie:
                cookie["expiry"] = int(time.time()) + 3600 * 24 * 30  # 30 days expiry

            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"Failed to add cookie {cookie.get('name', 'unknown')}: {e}")
        
        print("✅ Cookies successfully loaded!")
    except FileNotFoundError:
        print("⚠️ No cookies found. Logging in required.")
        sys.exit("Exiting script because cookies file not found.")


def save_cookies(driver):
    with open(COOKIE_FILE, "w") as file:
        json.dump(driver.get_cookies(), file, indent=4)
    print("✅ Cookies saved successfully.")

def auto_save_cookies(driver, interval=300):
    while True:
        time.sleep(interval)
        save_cookies(driver)
        print("🔄 Updated cookies saved to prevent logout!")

def is_youtube_logged_in(driver):
    try:
        # YouTube user profile icon (usually appears in the top right)
        driver.find_element(By.XPATH, "//button[@id='avatar-btn']")
        print("✅ User is logged in!")
        return True
    except Exception:
        print("⚠️ User is logged out!")
        return False

def refresh_auth_cookies(driver):
    """
    Refresh authentication cookies in a background tab to avoid interfering with video playback.
    """
    while True:
        time.sleep(900)  # Refresh every 15 minutes
        try:
            # Open a new background tab for refreshing cookies
            driver.execute_script("window.open('https://www.youtube.com/', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])
            wait_for_page_load(driver)
            time.sleep(2)
            save_cookies(driver)
            driver.close()  # Close the background tab
            driver.switch_to.window(driver.window_handles[0])  # Switch back to main tab
            print("✅ Authentication cookies refreshed in background tab!")
        except Exception as e:
            print(f"⚠️ Error refreshing cookies: {e}")

def click_on_sign_in(driver):
    try:
        # Wait for the "Sign in" button to be present
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@aria-label, 'Sign in')]"))
        )

        # Check if the button exists before clicking
        if sign_in_button and sign_in_button.is_displayed() and sign_in_button.is_enabled():
            sign_in_button.click()
            print("✅ Sign in button clicked.")
        else:
            print("⚠️ Sign in button exists but is not clickable.")

    except Exception as e:
        print("❌ Error: Sign in button not found or not clickable.", e)

def login_youtube(driver):
    driver.uc_open("https://www.youtube.com")
    # wait_for_page_load(driver)
    # time.sleep(2)
    # load_cookies(driver) # This is redundant?!
    # driver.refresh()
    wait_for_page_load(driver)
    time.sleep(2)
    if not is_youtube_logged_in(driver):
        print("🔑 Please log in manually...")
        # input("Press Enter after logging in...")
        sys.exit("Exiting script because the user is not logged in.")
        # save_cookies(driver)
    else:
        print("✅ Login successful with cookies!")

def force_reset_video(driver, attempts=5):
    """
    Force the video playback to start at 0 by repeatedly setting currentTime and ensuring it plays.
    """
    # Wait for any ad to finish
    while True:
        try:
            ad_playing = driver.execute_script(
                "return document.querySelector('.html5-video-player')?.classList.contains('ad-showing');"
            )
            if ad_playing:
                print("⏳ Ad is currently playing, waiting for it to finish...")
                time.sleep(3)
            else:
                print("✅ No ad playing. Resetting video playback.")
                break
        except Exception as e:
            print(f"⚠️ Error checking ad status: {e}")
            break

    # Reset the playback position to 0
    for i in range(attempts):
        try:
            video_element = driver.find_element(By.TAG_NAME, "video")  # Re-find the element here
            driver.execute_script("arguments[0].currentTime = 0;", video_element)
            current_time = driver.execute_script("return arguments[0].currentTime", video_element)
            if abs(current_time) < 0.1:
                print("🔄 Playback position successfully reset to 0.")
                break
            else:
                print(f"⏳ Attempt {i+1}: currentTime is {current_time}, trying to reset...")
                time.sleep(0.5)
        except Exception as e:
            print(f"⚠️ Error resetting video playback: {e}")
            break

    # Explicitly play the video after resetting playback position to 0
    try:
        play_button = driver.find_element(By.CLASS_NAME, "ytp-play-button")
        if play_button:
            play_button.click()  # Click play button
            print("▶️ Video playback started.")
    except Exception as e:
        print(f"❌ Error clicking the play button: {e}")

# def ensure_video_playing(driver):
#     """
#     Attempt to ensure the video is actually playing (not paused).
#     """
#     try:
#         video_element = driver.find_element(By.TAG_NAME, "video")
#         # If the video is paused, call play()
#         paused = driver.execute_script("return arguments[0].paused", video_element)
#         if paused:
#             print("⏯ Video is paused. Attempting to play...")
#             driver.execute_script("arguments[0].play()", video_element)
#             time.sleep(1)
#     except Exception as e:
#         print(f"⚠️ Could not ensure video is playing: {e}")

def wait_for_playlist_videos(driver, timeout=15):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//ytd-playlist-video-renderer//a[@id='video-title']"))
        )
        print("🎥 Videos loaded successfully!")
    except:
        print("⚠️ Timeout: No videos found.")

def ensure_video_playing(driver):
    """
    Waits for the page to fully load, checks if the video is paused, and if so,
    sends 'k' using ActionChains to play the video.
    """
    try:
        # Wait until the page is fully loaded
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.TAG_NAME, "html").is_displayed()
        )

        # Check if the video is paused by querying the <video> element
        paused = driver.execute_script(
            "var video = document.querySelector('video'); return video ? video.paused : null;"
        )
        
        if paused is None:
            print("⚠️ Could not find a video element.")
            return

        if paused:
            print("⏯ Video is paused. Pressing 'k' to play the video.")
            ActionChains(driver).send_keys("k").perform()
        else:
            print("🎥 Video is already playing.")

    except Exception as e:
        print(f"⚠️ Could not ensure video is playing: {e}")

def watch_playlist(driver, playlist_url):
    driver.uc_open(playlist_url)
    wait_for_page_load(driver)
    print("🎬 Loading playlist...")

    while True:
        try:
            scroll_like_human(driver)
            # mouse_element = driver.find_element(By.XPATH, "//button[@id='avatar-btn']")
            # # mouse_element = driver.find_element(By.XPATH, "//img[@id='img' and @alt='Avatar image']")
            # human_like_mouse_move(driver, mouse_element)
            # time.sleep(random.randint(3, 7))
            video_urls = [os.environ.get('VIDEO_URL')]
            if len(video_urls) > 0:
                print(f"✅ Found {len(video_urls)} videos in the playlist.")
                break
            else:
                print("❌ No videos found!")
        except Exception as e:
            print(f"❌ Error fetching video links: {e}")
            return
        
        # if not video_urls:
        #     print("❌ No videos found! Exiting...")
        #     return

    # Close any extraneous tabs such as the AdBlock installation page
    # close_adblock_tab(driver)

    for index, video_url in enumerate(video_urls):
        try:
            print(f"🎥 Playing video {index + 1}/{len(video_urls)}: {video_url}")
            driver.uc_open(video_url)
            wait_for_page_load(driver)
            driver.get_screenshot_as_file("WhyErrorAfterPageLoad.png")
            # Wait for video element to be present
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )

            # Force reset playback position repeatedly until it's 0
            force_reset_video(driver)

            # Wait until the video duration is available and ensure no ad is playing
            video_element = driver.find_element(By.TAG_NAME, "video")
            video_duration = None

            previous_video_url = driver.current_url

            # Monitor video playback
            stuck_attempts = 0
            while True:
                try:
                    # Check if an ad is playing
                    if driver.execute_script(
                        "return document.querySelector('.html5-video-player')?.classList.contains('ad-showing');"
                    ):
                        skip_button = driver.execute_script("return document.querySelector('.ytp-ad-skip-button')")
                        if skip_button:
                            driver.execute_script("document.querySelector('.ytp-ad-skip-button').click();")
                            print("⏭️ Skip Ad button clicked!")
                            time.sleep(1)
                        else:
                            print("⏳ Ad detected. Waiting for skip button or ad to finish...")
                        time.sleep(1)
                        continue

                    # Ensure the video element is still there and attempt to play
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "video"))
                    )
                    video_element = driver.find_element(By.TAG_NAME, "video")

                    # Make sure the video is not paused
                    ensure_video_playing(driver)
                    driver.get_screenshot_as_file("WhyError.png")
                    # 🖱️ Occasionally move the mouse like a human
                    if random.random() < 0.3:  # 30% chance
                        print("🖱️ Moving mouse slightly...")
                        move_mouse_randomly(driver)
                        time.sleep(random.uniform(1, 3))

                    # 📜 Occasionally scroll slightly (20% chance)
                    if random.random() < 0.2:
                        print("📜 Scrolling randomly like a human...")
                        scroll_like_human(driver)
                        time.sleep(random.uniform(2, 5))

                    # ⏸️ Occasionally pause & resume (15% chance)
                    if random.random() < 0.15:
                        print("⏸️ Pausing video briefly...")
                        pause_video_naturally(driver)
                        time.sleep(random.uniform(3, 8))  # User got distracted
                        print("▶️ Resuming video...")
                        ensure_video_playing(driver)

                    # 🔊 Occasionally adjust volume (10% chance)
                    if random.random() < 0.1:
                        print("🔊 Adjusting volume slightly...")
                        adjust_volume_randomly(driver)
                        time.sleep(random.uniform(1, 2))

                    current_time = driver.execute_script("return arguments[0].currentTime", video_element)
                    video_duration = driver.execute_script("return arguments[0].duration", video_element)

                    if current_time is None or video_duration is None or video_duration == 0:
                        stuck_attempts += 1
                        print("⏳ Waiting for video playback details...")
                        time.sleep(2)
                        if stuck_attempts > 5:
                            print("⚠️ Could not retrieve valid playback info. Skipping to next video...")
                            break
                        continue
                    else:
                        stuck_attempts = 0  # reset

                    print(f"📺 Video Title: {driver.title}")
                    print(f"⏱️ Video Length: {video_duration} seconds")
                    print(f"🕒 Time Watched: {current_time} seconds")

                    exit_script()

                    if current_time >= video_duration:
                        print(f"✅ Video {index + 1} has finished.")
                        break

                    if driver.current_url != previous_video_url:
                        print(f"🔄 Video changed! Now playing: {driver.current_url}")
                        previous_video_url = driver.current_url

                    time.sleep(5)
                except Exception as e:
                    print(f"⚠️ Error during video playback monitoring: {e}")
                    break

            print("➡️ Moving to the next video in the playlist...")

        except Exception as e:
            print(f"❌ Error while playing video {index + 1}: {e}")
            print("⏩ Retrying next video...")

if __name__ == "__main__":
    playlist_url = os.environ.get('PLAYLIST_URL')

    driver = get_driver()
    login_youtube(driver)

    while True:
      try:
          watch_playlist(driver, playlist_url)
      except Exception as e:
          print(f"An error occurred: {e}")
          time.sleep(5)  # Optional: wait a bit before retrying
      finally:
          driver.quit()
          driver = get_driver()  # Reinitialize the driver if needed
          login_youtube(driver)  # Ensure login before retrying
