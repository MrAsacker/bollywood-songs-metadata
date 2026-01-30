import pandas as pd
import os

# --- CONFIGURATION ---
# Match these filenames to the ones you just created
ALBUMS_FILE = "myswar_albums_2005_2014.csv"
SONGS_FILE = "myswar_songs_2005_2014.csv"

def clean_csv(filename, unique_col):
    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        return

    print(f"--- Cleaning {filename} ---")
    
    # 1. Load Data
    df = pd.read_csv(filename)
    original_count = len(df)
    
    # 2. Drop Duplicates
    # We keep the 'first' occurrence and drop the rest
    df_cleaned = df.drop_duplicates(subset=[unique_col], keep='first')
    
    final_count = len(df_cleaned)
    removed_count = original_count - final_count
    
    # 3. Save Back
    # We save to a new file just to be safe
    clean_filename = filename.replace(".csv", "_CLEANED.csv")
    df_cleaned.to_csv(clean_filename, index=False)
    
    print(f"   Original Rows: {original_count}")
    print(f"   Duplicate Rows Removed: {removed_count}")
    print(f"   Final Unique Rows: {final_count}")
    print(f"✅ Saved clean version to: {clean_filename}\n")

# Run the cleaning
if __name__ == "__main__":
    # Clean Albums (Unique by 'album_uuid')
    clean_csv(ALBUMS_FILE, "album_uuid")
    
    # Clean Songs (Unique by 'song_uuid')
    clean_csv(SONGS_FILE, "song_uuid")