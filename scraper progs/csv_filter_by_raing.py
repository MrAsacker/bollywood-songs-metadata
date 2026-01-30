import os
import pandas as pd

# --- CONFIGURATION ---
INPUT_FOLDER = 'filtered_data'                  # Folder containing your original CSVs
OUTPUT_FOLDER = 'filtered_data/best_rated_csvs' # Folder where the new CSVs will appear

# FILTERS
RATING_COL = 'song_rating'       
RATING_THRESHOLD = 4.3

# Create the output folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- PROCESSING LOOP ---
def run_csv_filtering():
    print(f"Scanning folder: {INPUT_FOLDER}...\n")
    
    # Get list of all CSV files in the folder
    files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith('.csv')]
    
    if not files:
        print("No CSV files found.")
        return

    processed_count = 0

    for filename in files:
        input_path = os.path.join(INPUT_FOLDER, filename)
        
        # We use the EXACT same filename for the destination
        output_path = os.path.join(OUTPUT_FOLDER, filename) 

        try:
            # 1. Read the CSV
            df = pd.read_csv(input_path)
            
            # Check if rating column exists
            if RATING_COL not in df.columns:
                print(f"[SKIP] '{filename}' - Column '{RATING_COL}' missing.")
                continue

            # Ensure numeric
            df[RATING_COL] = pd.to_numeric(df[RATING_COL], errors='coerce')

            # 2. Filter (Rating >= 4.3)
            filtered_df = df[df[RATING_COL] >= RATING_THRESHOLD]

            # 3. Save as a separate file
            if not filtered_df.empty:
                filtered_df.to_csv(output_path, index=False)
                print(f"[CREATED] {filename}")
                print(f"    - Kept {len(filtered_df)} of {len(df)} songs")
                processed_count += 1
            else:
                print(f"[INFO] {filename} - No songs rated >= {RATING_THRESHOLD}")

        except Exception as e:
            print(f"[ERROR] processing {filename}: {e}")

    print("-" * 30)
    print(f"Done. {processed_count} filtered CSVs created in '{OUTPUT_FOLDER}'.")

if __name__ == "__main__":
    run_csv_filtering()