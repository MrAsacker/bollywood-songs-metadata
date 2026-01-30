import os
import re
import time
import random
import logging
import pandas as pd
import yt_dlp   

# --- 1. CONFIGURATION ---
START = 1955
END = 1964
INPUT_CSV = f'tobe_songs_{START}_{END}_final.csv'
OUTPUT_CSV = f"status_{INPUT_CSV}" # Tracks progress (Resumable)
DOWNLOAD_DIR = f'downloads/songs/songs_{START}_{END}'
LOG_FILE = f"log_{INPUT_CSV.replace('.csv', '.log')}"
FFMPEG_DIR = r"C:\ffmpeg\bin"    # Your identified path

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Logging configuration
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- 2. UTILITY FUNCTIONS ---

def sanitize_filename(name):
    """Safety for Windows filesystems."""
    name = re.sub(r'[\\/*?:"<>|]', "", str(name))
    name = re.sub(r'\s+', ' ', name).strip()
    return name[:100]

def get_best_url(row):
    """Finds first valid URL in your CSV columns."""
    cols = ['music_yt_url_1', 'music_yt_url_2',  'youtube_url', 'music_yt_url_3']
    for col in cols:
        if col in row and pd.notna(row[col]):
            url = str(row[col]).strip()
            if url.startswith('http'):
                return url
    return None

def extract_video_id(url):
    """For your hobby site: <img src='https://img.youtube.com/vi/ID/maxresdefault.jpg'>"""
    if not url: return ""
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else ""

# --- 3. THE CORE PROCESSOR ---

def run_production():
    # Verify FFmpeg before starting
    if not os.path.exists(os.path.join(FFMPEG_DIR, "ffmpeg.exe")):
        print(f"CRITICAL ERROR: ffmpeg.exe not found at {FFMPEG_DIR}")
        return

    # Load / Resume
    if os.path.exists(OUTPUT_CSV):
        df = pd.read_csv(OUTPUT_CSV)
        print(f"Resuming {INPUT_CSV} progress...")
    else:
        df = pd.read_csv(INPUT_CSV)
        df['download_status'] = 'pending'
        df['yt_video_id'] = ''

    total = len(df)

    for index, row in df.iterrows():
        if row['download_status'] == 'downloaded':
            continue

        url = get_best_url(row)
        if not url:
            df.at[index, 'download_status'] = 'no_url'
            continue

        video_id = extract_video_id(url)
        df.at[index, 'yt_video_id'] = video_id

        # File naming: [uuid]_[title].mp3
        s_title = row.get('song_title', 'unknown')
        s_uuid = row.get('song_uuid', 'no_uuid')
        filename = f"{s_uuid}_{sanitize_filename(s_title)}"
        filepath = os.path.join(DOWNLOAD_DIR, filename)

        print(f"[{index+1}/{total}] Downloading: {s_title}")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{filepath}.%(ext)s',
            'overwrites': False,
            'ffmpeg_location': FFMPEG_DIR,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128', # Small size, high compatibility
            }],
            'quiet': True,
            'no_warnings': True,
        }

        success = False
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if ydl.download([url]) == 0:
                    success = True
        except Exception as e:
            err = str(e)
            logging.error(f"UUID {s_uuid} Failed: {err}")
            if "404" in err or "unavailable" in err:
                df.at[index, 'download_status'] = 'failed_dead_link'
            else:
                df.at[index, 'download_status'] = 'failed_network'

        if success:
            df.at[index, 'download_status'] = 'downloaded'

        # Batch save every 10 songs for data safety
        if index % 10 == 0:
            df.to_csv(OUTPUT_CSV, index=False)
            time.sleep(random.uniform(1, 2)) # Jitter to avoid bot detection

    # Final Save
    df.to_csv(OUTPUT_CSV, index=False)
    print("\n--- Processing Finished ---")

if __name__ == "__main__":
    run_production()