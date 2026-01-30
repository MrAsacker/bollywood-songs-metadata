import os
import re
import shutil
import pandas as pd

# --- CONFIGURATION ---
start = 2015
end = 2025
INPUT_CSV = f'filtered_data/tobe_songs_{start}_{end}_final.csv'    
SOURCE_DIR = f'downloads/songs/songs_{start}_{end}'   
DEST_DIR = f'downloads/songs/best_of_{start}_{end}'   

# UPDATED: Matches your specific CSV header 'song_rating'
RATING_COL = 'song_rating'       
RATING_THRESHOLD = 4.3

# Create destination folder
os.makedirs(DEST_DIR, exist_ok=True)

# --- UTILITY (Must match your downloader exactly) ---
def sanitize_filename(name):
    """
    Exact copy of the sanitization logic from the downloader 
    to ensure we find the correct files.
    """
    name = re.sub(r'[\\/*?:"<>|]', "", str(name))
    name = re.sub(r'\s+', ' ', name).strip()
    return name[:100]

# --- MAIN PROCESS ---
def process_top_rated():
    # 1. Load Data
    print(f"Loading {INPUT_CSV}...")
    try:
        df = pd.read_csv(INPUT_CSV)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return
    
    # Ensure rating is numeric (handles strings like "4.5" or missing data)
    df[RATING_COL] = pd.to_numeric(df[RATING_COL], errors='coerce')
    
    # 2. Filter Data
    # Get songs that match criteria AND have a UUID (needed for filename)
    top_songs = df[
        (df[RATING_COL] >= RATING_THRESHOLD) & 
        (df['song_uuid'].notna())
    ]
    
    print(f"Found {len(top_songs)} songs with {RATING_COL} >= {RATING_THRESHOLD}")
    
    copied_count = 0
    missing_count = 0
    
    # 3. Iterate and Copy
    for index, row in top_songs.iterrows():
        # Reconstruct the expected filename
        s_title = row.get('song_title', 'unknown')
        s_uuid = row.get('song_uuid')
        
        clean_title = sanitize_filename(s_title)
        
        # Expected filename format: UUID_Title.mp3
        filename = f"{s_uuid}_{clean_title}.mp3"
        
        src_path = os.path.join(SOURCE_DIR, filename)
        dst_path = os.path.join(DEST_DIR, filename)
        
        if os.path.exists(src_path):
            try:
                # copy2 preserves metadata (creation time, etc.)
                shutil.copy2(src_path, dst_path)
                copied_count += 1
            except Exception as e:
                print(f"Error copying {filename}: {e}")
        else:
            missing_count += 1

    print("-" * 30)
    print(f"Process Complete.")
    print(f"Total Eligible Songs: {len(top_songs)}")
    print(f"Successfully Copied:  {copied_count}")
    print(f"Files Not Found:      {missing_count}")
    print(f"Files located in:     {DEST_DIR}")

if __name__ == "__main__":
    process_top_rated()