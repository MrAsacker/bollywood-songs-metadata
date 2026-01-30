import csv
import uuid
import time
import sys
import os
import re
import random
from bs4 import BeautifulSoup

# --- SELENIUM IMPORTS ---
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- COLORS FOR CONSOLE ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

# --- CONFIGURATION (RESUME SETTINGS) ---
START_YEAR = 1931
START_PAGE = 1      
END_YEAR = 1944

# Dynamic filenames
ALBUMS_CSV = f"myswar_albums_{START_YEAR}_{END_YEAR}.csv"
SONGS_CSV = f"myswar_songs_{START_YEAR}_{END_YEAR}.csv"
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

# --- GLOBAL CACHE FOR DRIVER ---
CACHED_DRIVER_PATH = None

# --- HEADERS ---
ALBUM_HEADERS = [
    "album_uuid", "album_title", "album_year", "album_category",
    "album_music_director", "album_lyricist", "album_label", 
    "album_rating"
]

SONG_HEADERS = [
    "song_uuid", "album_uuid", 
    "track_number", "song_title", "song_singers", 
    "song_rating", "youtube_url"
]

def setup_driver():
    """Starts a visible browser (Off-Screen) using cached driver path"""
    global CACHED_DRIVER_PATH

    chrome_options = Options()
    chrome_options.binary_location = BRAVE_PATH
    
    # --- ANTI-DETECTION FLAGS ---
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.add_argument("--mute-audio")
    
    # --- MULTITASKING FIX: MOVE WINDOW OFF-SCREEN ---
    chrome_options.add_argument("--window-position=-10000,0") 
    chrome_options.add_argument("--window-size=1920,1080")
    
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    
    if CACHED_DRIVER_PATH is None:
        print(f"{Colors.CYAN}  [INIT] Checking/Downloading ChromeDriver...{Colors.RESET}")
        try:
            CACHED_DRIVER_PATH = ChromeDriverManager().install()
        except Exception as e:
            print(f"{Colors.RED}  [ERROR] Failed to check driver updates: {e}{Colors.RESET}")
            raise e

    service = Service(CACHED_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(45)
    return driver

def restart_driver(driver):
    """Force kills the browser and starts a new one to clear memory"""
    print(f"{Colors.YELLOW}  [MAINTENANCE] Restarting Browser (Off-Screen) to clear memory...{Colors.RESET}")
    try: driver.quit()
    except: pass
    time.sleep(random.uniform(2.0, 4.0)) 
    return setup_driver()

def get_text_from_label(soup_element, label_text):
    label_span = soup_element.find('span', class_='attribute_lable', string=lambda t: t and label_text in t)
    if label_span:
        value_span = label_span.find_next_sibling('span', class_='attribute_value')
        if value_span: return value_span.text.strip()
    return ""

def extract_rating(soup_container):
    target_span = None
    try:
        label = soup_container.find("span", class_="attribute_lable", string=lambda t: t and "Overall Rating" in t)
        if label:
            target_span = label.find_next_sibling("span", class_="attribute_value")
    except: pass

    if not target_span:
        try:
            input_tag = soup_container.find("input", {"name": "score"})
            if input_tag: target_span = input_tag.find_parent("span")
        except: pass

    if not target_span: return "0"

    try:
        input_tag = target_span.find("input", {"name": "score"})
        if input_tag and input_tag.has_attr("value"):
            val = input_tag["value"].strip()
            if val:
                try: return str(round(float(val), 2))
                except: return val
    except: pass

    try:
        title_text = target_span.get("title", "").strip().lower()
        if "not enough ratings" in title_text: return "0"
        if "bad" in title_text: return "1"
        if "poor" in title_text: return "2"
        if "average" in title_text: return "3"
        if "good" in title_text: return "4"
        if "great" in title_text: return "5"
    except: pass

    return "0"

def scrape_inner_songs(driver, attempt=1):
    valid_songs = []
    album_rating = "0"

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "song_detail_display_table")))
        try: driver.execute_script("window.stop();")
        except: pass
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        main_block = soup.find('div', class_='album_left') 
        if main_block: album_rating = extract_rating(main_block)
        else: album_rating = extract_rating(soup)

        song_tables = soup.find_all('table', class_='song_detail_display_table')
        
        for index, table in enumerate(song_tables, start=1):
            yt_link_tag = table.find('a', href=lambda h: h and "youtube" in h)
            if not yt_link_tag: continue 

            valid_songs.append({
                "track": index, 
                "title": table.find('a', class_='songs_like_this2').text.strip() if table.find('a', class_='songs_like_this2') else "Unknown", 
                "singers": get_text_from_label(table, "Singer"),
                "rating": extract_rating(table), 
                "url": yt_link_tag['href']
            })
            
    except Exception:
        if attempt == 1:
            try: driver.refresh()
            except: pass
            time.sleep(random.uniform(3.0, 5.0)) 
            return scrape_inner_songs(driver, attempt=2)
            
    return album_rating, valid_songs

def scrape_main():
    os.system('color')
    
    albums_exist = os.path.exists(ALBUMS_CSV)
    songs_exist = os.path.exists(SONGS_CSV)
    
    driver = None
    try:
        driver = setup_driver()
    except Exception as e:
        print(f"{Colors.RED}[CRITICAL] Driver failed: {e}{Colors.RESET}")
        return

    with open(ALBUMS_CSV, "a", newline="", encoding="utf-8") as f_albums, \
         open(SONGS_CSV, "a", newline="", encoding="utf-8") as f_songs:
        
        writer_albums = csv.DictWriter(f_albums, fieldnames=ALBUM_HEADERS)
        writer_songs = csv.DictWriter(f_songs, fieldnames=SONG_HEADERS)
        
        if not albums_exist: writer_albums.writeheader()
        if not songs_exist: writer_songs.writeheader()

        processed_count = 0 

        for year in range(START_YEAR, END_YEAR + 1):
            print(f"{Colors.HEADER}--- Processing Year: {year} ---{Colors.RESET}")
            
            # --- RESUME LOGIC ---
            # If we are on the START_YEAR, use the custom START_PAGE.
            # Otherwise (for 1990, 1991...), start at 1.
            if year == START_YEAR:
                page_count = START_PAGE
            else:
                page_count = 1
                
            last_page_first_album = "" 
            
            while True:
                if page_count == 1:
                    target_url = f"https://myswar.co/album/year/{year}"
                else:
                    target_url = f"https://myswar.co/album/year/{year}/{page_count}?album_type=&album_filter_years=&album_filter_labels=&album_filter_md=&album_filter_lyricist=&album_filter_album_artist=&ut=3"
                
                print(f"  --> Scraping Page {Colors.RED}{page_count}{Colors.RESET} ..............................................")

                # --- PAGE LOAD (Safe Retry) ---
                load_success = False
                for _ in range(3):
                    try:
                        driver.get(target_url)
                        load_success = True
                        break
                    except Exception:
                        print(f"{Colors.YELLOW}      [WARN] Timeout. Reloading...{Colors.RESET}")
                        driver = restart_driver(driver)
                
                if not load_success:
                    print(f"{Colors.RED}      [ERROR] Could not load Page {page_count}. Skipping year.{Colors.RESET}")
                    break

                time.sleep(random.uniform(4.5, 6.5)) 
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                album_tables = soup.find_all('table', class_='song_detail_display_table')
                
                if len(album_tables) == 0:
                    print(f"{Colors.BLUE}  [INFO] No albums found. Finished Year {year}.{Colors.RESET}")
                    break

                try:
                    first_tag = album_tables[0].find('a', class_='songs_like_this2')
                    if first_tag:
                        current_first_album = first_tag.text.strip()
                        if current_first_album == last_page_first_album:
                            print(f"{Colors.BLUE}  [INFO] Duplicate Page Detected (Redirect Loop). Finished Year {year}.{Colors.RESET}")
                            break
                        last_page_first_album = current_first_album
                except: pass

                main_window = driver.current_window_handle
                
                for table in album_tables:
                    processed_count += 1
                    
                    # --- MAINTENANCE RELOAD (Safe Retry) ---
                    if processed_count % 15 == 0:
                        driver = restart_driver(driver)
                        reload_ok = False
                        for _ in range(3):
                            try:
                                driver.get(target_url)
                                reload_ok = True
                                break
                            except:
                                driver = restart_driver(driver)
                        
                        if not reload_ok: break
                        main_window = driver.current_window_handle
                        time.sleep(random.uniform(2.0, 3.0))

                    title_tag = table.find('a', class_='songs_like_this2')
                    if not title_tag: continue
                    
                    album_title = title_tag.text.strip()
                    album_url = title_tag['href']
                    
                    try:
                        driver.execute_script("window.open(arguments[0], '_blank');", album_url)
                        driver.switch_to.window(driver.window_handles[-1])
                        album_rating, valid_songs = scrape_inner_songs(driver)
                        driver.close()
                        driver.switch_to.window(main_window)
                    except Exception as e:
                        print(f"{Colors.RED}      [SKIP - ERROR] {album_title}: {e}{Colors.RESET}")
                        try:
                            while len(driver.window_handles) > 1:
                                driver.switch_to.window(driver.window_handles[-1])
                                driver.close()
                            driver.switch_to.window(main_window)
                        except: driver = restart_driver(driver)
                        continue

                    if not valid_songs:
                        print(f"{Colors.RED}      [SKIP] {album_title} (0 YouTube Links){Colors.RESET}")
                        continue

                    print(f"{Colors.GREEN}      [SAVE] {album_title} | Rating: {album_rating} | Songs: {len(valid_songs)}{Colors.RESET}")

                    unique_album_string = f"{album_title}_{year}".lower().strip()
                    current_album_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_album_string))

                    writer_albums.writerow({
                        "album_uuid": current_album_uuid,
                        "album_title": album_title,
                        "album_year": year,
                        "album_category": get_text_from_label(table, "Album Category"),
                        "album_music_director": get_text_from_label(table, "Music Director"),
                        "album_lyricist": get_text_from_label(table, "Lyricist"),
                        "album_label": get_text_from_label(table, "Label"),
                        "album_rating": album_rating
                    })

                    for song in valid_songs:
                        unique_song_string = f"{current_album_uuid}_{song['track']}_{song['title']}".lower().strip()
                        song_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_song_string))

                        writer_songs.writerow({
                            "song_uuid": song_uuid,
                            "album_uuid": current_album_uuid,
                            "track_number": song['track'],
                            "song_title": song['title'],
                            "song_singers": song['singers'],
                            "song_rating": song['rating'],
                            "youtube_url": song['url']
                        })
                    
                    f_albums.flush()
                    f_songs.flush()
                    time.sleep(random.uniform(0.5, 1.5)) 

                if len(album_tables) < 24:
                    print(f"{Colors.BLUE}  [INFO] Last page reached for {year}.{Colors.RESET}")
                    break
                
                page_count += 1
    
    if driver: driver.quit()
    print(f"{Colors.GREEN}--- SCRAPING COMPLETE ---{Colors.RESET}")

if __name__ == "__main__":
    scrape_main()