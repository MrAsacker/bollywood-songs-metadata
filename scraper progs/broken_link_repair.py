import pandas as pd
import yt_dlp
import time
import sys

# --- CONFIGURATION ---
API_DELAY_SECONDS = 2  # Matches your Node.js delay

# --- COLORS ---
class Colors:
    HEADER = '\033[95m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# --- INITIALIZE TOOLS ---
# We use 'extract_flat': True. This is the secret sauce. 
# It tells yt-dlp: "Just read the search page. DO NOT check the video stream."
ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'noplaylist': True,
    'extract_flat': True, # <--- THIS MAKES IT FAST (Like the Node script)
    'default_search': 'ytsearch1', # Only ask for 1 result
}

# --- HELPER FUNCTIONS ---

def get_video_fast(query):
    """
    Searches YouTube and returns the first Video ID found.
    Does NOT check if the video is playable (for maximum speed).
    """
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # This runs instantly because it only looks at metadata
            info = ydl.extract_info(query, download=False)
            
            if 'entries' in info and info['entries']:
                # Return the URL of the first result
                return info['entries'][0]['url']
            
    except Exception:
        return None
    return None

# --- MAIN SCRIPT ---

try:
    print(f"{Colors.BOLD}Loading CSV files...{Colors.RESET}")
    df_songs = pd.read_csv('myswar_songs_1945_1954.csv')
except Exception as e:
    print(f"{Colors.RED}CRITICAL ERROR: {e}{Colors.RESET}")
    sys.exit(1)

indices_to_drop = []

print(f"{'='*100}")
print(f"{Colors.BOLD}{'STATUS':<10} | {'SONG NAME':<35} | {'DETAILS'}{Colors.RESET}")
print(f"{'='*100}")

for index, row in df_songs.iterrows():
    try:
        song_name = str(row['song_title'])
        display_name = (song_name[:33] + "..") if len(song_name) > 33 else song_name
        current_url = row['youtube_url']
        singer = str(row['song_singers'])
        if singer.lower() == 'nan': singer = ""

        # --- STEP 1: SKIP IF WE HAVE A LINK (Basic check) ---
        # The Node script doesn't check validity, so we just check if text exists.
        if pd.notna(current_url) and "youtube.com" in str(current_url):
            print(f"{Colors.GREEN}[OK]       {Colors.RESET}| {display_name:<35} | Has link")
            continue

        # --- STEP 2: SEARCH (The Fast Way) ---
        print(f"{Colors.YELLOW}[SEARCH]   {Colors.RESET}| {display_name:<35} | Searching...", end="\r")
        
        # Query: "Song Name Singer Name" (Simple & Effective)
        query = f"{song_name} {singer}"
        
        new_link = get_video_fast(query)

        # Clear the "Searching..." line
        print(f"{' '*100}", end="\r")

        # --- STEP 3: UPDATE ---
        if new_link:
            df_songs.at[index, 'youtube_url'] = new_link
            print(f"{Colors.CYAN}[FIXED]    {Colors.RESET}| {display_name:<35} | {Colors.CYAN}Found: {new_link}{Colors.RESET}")
        else:
            # If fast search fails, mark for delete
            indices_to_drop.append(index)
            print(f"{Colors.RED}[DELETE]   {Colors.RESET}| {display_name:<35} | {Colors.RED}No results.{Colors.RESET}")

        # The delay is critical to avoid 429 errors (Too Many Requests)
        time.sleep(API_DELAY_SECONDS)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[STOP]     Script stopped. Saving data...{Colors.RESET}")
        break
    except Exception as e:
        print(f"{Colors.RED}[ERROR]    {e}{Colors.RESET}")

# --- SAVE ---
if indices_to_drop:
    df_songs.drop(indices_to_drop, inplace=True)
    print(f"\n{Colors.RED}[INFO]     Removed {len(indices_to_drop)} songs.{Colors.RESET}")

df_songs.to_csv('songs_updated_fast.csv', index=False)
print(f"{Colors.GREEN}[DONE]     Saved to songs_updated_fast.csv{Colors.RESET}")