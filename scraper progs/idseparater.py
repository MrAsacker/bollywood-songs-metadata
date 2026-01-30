import os
import re
import pandas as pd

# --- CONFIGURATION ---
# Input: The folder where you saved the >= 4.3 CSVs in the previous step
INPUT_FOLDER = 'filtered_data_4.3'

# Output: New folder for the CSVs that have the IDs added
OUTPUT_FOLDER = 'filtered_data_4.3/final_with_ids'

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- UTILITY: ID Extractor ---
def extract_video_id(url):
    """
    Extracts the 11-character YouTube Video ID from a URL.
    Works for:
    - https://www.youtube.com/watch?v=dQw4w9WgXcQ
    - https://youtu.be/dQw4w9WgXcQ
    - https://music.youtube.com/watch?v=dQw4w9WgXcQ
    """
    if pd.isna(url) or str(url).strip() == '':
        return ""
    
    url = str(url).strip()
    # Regex checks for 'v=' or short URL format
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    if match:
        return match.group(1)
    return ""

# --- MAIN PROCESS ---
def process_ids():
    print(f"Scanning {INPUT_FOLDER}...\n")
    
    files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith('.csv')]
    
    if not files:
        print("No CSV files found to process.")
        return

    processed_count = 0

    for filename in files:
        input_path = os.path.join(INPUT_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, filename)

        try:
            df = pd.read_csv(input_path)
            
            # --- CREATE NEW COLUMNS ---
            # We use .apply() to run the extractor on every row
            
            # 1. youtube_url -> youtubeurlid
            if 'youtube_url' in df.columns:
                df['youtubeurlid'] = df['youtube_url'].apply(extract_video_id)
            else:
                df['youtubeurlid'] = "" # Create empty col if original missing

            # 2. music_yt_url_1 -> musicurlid1
            if 'music_yt_url_1' in df.columns:
                df['musicurlid1'] = df['music_yt_url_1'].apply(extract_video_id)
            else:
                df['musicurlid1'] = ""

            # 3. music_yt_url_2 -> musicurlid2
            if 'music_yt_url_2' in df.columns:
                df['musicurlid2'] = df['music_yt_url_2'].apply(extract_video_id)
            else:
                df['musicurlid2'] = ""

            # 4. music_yt_url_3 -> musicurlid3
            if 'music_yt_url_3' in df.columns:
                df['musicurlid3'] = df['music_yt_url_3'].apply(extract_video_id)
            else:
                df['musicurlid3'] = ""

            # --- SAVE ---
            df.to_csv(output_path, index=False)
            print(f"[PROCESSED] {filename}")
            processed_count += 1

        except Exception as e:
            print(f"[ERROR] Could not process {filename}: {e}")

    print("-" * 30)
    print(f"Done. Processed {processed_count} files.")
    print(f"New CSVs are in: {OUTPUT_FOLDER}")

if __name__ == "__main__":
    process_ids()