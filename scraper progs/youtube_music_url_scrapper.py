import pandas as pd
from ytmusicapi import YTMusic
from tqdm import tqdm
from thefuzz import fuzz
import time
import os
import random
import re 
import sys 

# ==============================================================================
# ⚙️ CONFIGURATION
# ==============================================================================
START = 1950
END = 1960
INPUT_CSV = f'tobe_songs_{START}_{END}.csv'         
AUTH_FILE = 'browser01.json'       
BATCH_SIZE = 20                  
BAD_KEYWORDS = ['cover', 'karaoke', 'instrumental', 'remix', 'lofi', 'slowed', 'reverb', 'bass boosted']

# ==============================================================================

OUTPUT_CSV = INPUT_CSV.replace('.csv', '_final.csv')

# 1. AUTHENTICATION & PRE-CHECK (From your script - Good idea!)
if os.path.exists(AUTH_FILE):
    print(f"\n✅ Authenticated successfully using: {AUTH_FILE}")
    yt = YTMusic(AUTH_FILE)
else:
    print(f"\n⚠️  {AUTH_FILE} not found. Running ANONYMOUSLY.")
    yt = YTMusic()

# ⚡ Pre-flight check: Ensure cookies work BEFORE starting the loop
try:
    yt.get_library_playlists() # Quick ping to check auth
except Exception:
    print(f"\n❌ FATAL ERROR: Cookies in {AUTH_FILE} are invalid or expired.")
    print("👉 Please extract new cookies and update the JSON file.")
    sys.exit(1)

# ------------------------------------------------------------------------------

def search_and_verify(query, title_to_match, seen_ids):
    valid_links = []
    
    # 🛡️ NETWORK GUARD (From my script - Critical for long runs)
    while True: 
        try:
            results = yt.search(query)[:4] 
            
            # --- Success! Process results ---
            for index, item in enumerate(results):
                res_type = item.get('resultType')
                
                if res_type in ['song', 'video']:
                    video_id = item.get('videoId')
                    video_title = item.get('title', '')
                    
                    # Smart Scoring
                    score = fuzz.token_set_ratio(title_to_match, video_title)
                    if res_type == 'song': score += 5  
                    
                    lower_title = video_title.lower()
                    for kw in BAD_KEYWORDS:
                        if kw in lower_title:
                            score -= 15 
                            break 
                    
                    required_score = 45 if index == 0 else 60
                    
                    if score < required_score:
                        continue 
                    
                    if video_id and video_id not in seen_ids:
                        seen_ids.add(video_id)
                        valid_links.append(f"https://music.youtube.com/watch?v={video_id}")
            break # Break retry loop on success

        except Exception as e:
            error_msg = str(e)
            
            # 🚨 Cookies Expired -> STOP
            if "401" in error_msg or "Unauthorized" in error_msg:
                print(f"\n❌ FATAL ERROR: Cookies Expired! Please update {AUTH_FILE}.")
                sys.exit(1)
            
            # ⚠️ Internet Down -> WAIT
            # We wait here instead of crashing, so you don't lose progress.
            pbar_msg = f"⚠️ Connection Lost: {error_msg[:20]}..."
            print(f"\n{pbar_msg}")
            time.sleep(20) # Wait 20s and retry same query
            
    return valid_links

def get_music_links(title, singer):
    # We use Sequential Logic (My script) because it saves API calls.
    # Parallel (Your script) hits rate limits faster.
    try:
        links = []
        seen_ids = set()

        match = re.search(r'\((.*?)\)', title)
        has_alias = False
        main_title = title
        alias_title = ""

        if match:
            has_alias = True
            alias_title = match.group(1).strip()
            main_title = re.sub(r'\(.*?\)', '', title).strip()

        # 🔍 SEARCH 1: Main Title
        query_1 = f"{main_title} {singer}"
        links.extend(search_and_verify(query_1, main_title, seen_ids))

        # ⚡ OPTIMIZATION: Only search alias if Main Search found NOTHING
        if has_alias and len(links) == 0:
            query_2 = f"{alias_title} {singer}"
            links.extend(search_and_verify(query_2, alias_title, seen_ids))

        links = links[:3]
        while len(links) < 3:
            links.append("")
            
        return links

    except Exception:
        return ["", "", ""] 

def process_csv():
    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"❌ Error: Could not find file '{INPUT_CSV}'")
        return

    start_index = 0
    if os.path.exists(OUTPUT_CSV):
        df_done = pd.read_csv(OUTPUT_CSV, on_bad_lines='skip')
        start_index = len(df_done)
        print(f"🔄 Resuming {INPUT_CSV} from row {start_index}...")
    else:
        empty_df = pd.DataFrame(columns=list(df.columns) + ['music_yt_url_1', 'music_yt_url_2', 'music_yt_url_3'])
        empty_df.to_csv(OUTPUT_CSV, index=False)
        print(f"🚀 Starting new job for: {INPUT_CSV} ({len(df)} songs)")

    total_rows = len(df)
    if start_index >= total_rows:
        print("✅ File already completed!")
        return

    buffer = []
    session_counter = 0 
    next_micro_break = random.randint(80, 120)    
    next_coffee_break = random.randint(800, 1200) 

    print("-" * 60) 

    # ncols=100 ensures no staircase effect
    pbar = tqdm(range(start_index, total_rows), initial=start_index, total=total_rows, unit="song", ncols=100)
    
    for i in pbar:
        row = df.iloc[i].copy()
        
        # Clean title for display
        title = str(row.get('song_title', '')).strip().replace('\n', ' ').replace('\r', '')
        singer = str(row.get('song_singers', '')).strip()
        
        short_title = (title[:20] + '..') if len(title) > 20 else title.ljust(22)
        pbar.set_description(f"🔎 {short_title}")
        
        links = get_music_links(title, singer)

        row['music_yt_url_1'] = links[0]
        row['music_yt_url_2'] = links[1]
        row['music_yt_url_3'] = links[2]
        
        buffer.append(row)

        if len(buffer) >= BATCH_SIZE:
            pd.DataFrame(buffer).to_csv(OUTPUT_CSV, mode='a', header=False, index=False)
            buffer = [] 

        session_counter += 1
        if session_counter >= next_micro_break:
            pause_time = random.uniform(10, 20) 
            pbar.write(f"   💤 Micro-break: {int(pause_time)}s...") 
            time.sleep(pause_time)
            session_counter = 0 
            next_micro_break = random.randint(80, 120)
        
        if i > 0 and i % next_coffee_break == 0:
            long_pause = random.uniform(60, 120)
            mins = int(long_pause/60)
            pbar.write(f"\n   ☕ COFFEE BREAK: {mins} mins.\n")
            time.sleep(long_pause)
            next_coffee_break = random.randint(800, 1200)

        # ⚡ SAFETY SLEEP: 1.2s - 2.5s 
        # (0.5s is too risky for long jobs)
        time.sleep(random.uniform(1.2, 2.5))

    if buffer:
        pd.DataFrame(buffer).to_csv(OUTPUT_CSV, mode='a', header=False, index=False)

    pbar.close()
    print("-" * 60)
    print(f"🎉 JOB DONE! All data saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    process_csv()
