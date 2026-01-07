import pandas as pd
import os

file_path = "data/new data/MEO_Details.xlsx"
print(f"Checking file: {file_path}")

if not os.path.exists(file_path):
    print("File not found!")
    exit()

try:
    df = pd.read_excel(file_path)
    print("Columns:", df.columns.tolist())
    
    # Search for Jainad
    query = "jainad"
    print(f"\nSearching for '{query}' in BLKNAME...")
    
    if 'BLKNAME' in df.columns:
        # Check exact matches
        matches = df[df['BLKNAME'].astype(str).str.strip().str.lower() == query]
        if not matches.empty:
            print("Found exact match in BLKNAME:")
            print(matches.iloc[0])
        else:
            print("No exact match in BLKNAME.")
            
            # Fuzzy check
            import difflib
            all_mandals = df['BLKNAME'].astype(str).str.strip().str.lower().tolist()
            close_matches = difflib.get_close_matches(query, all_mandals, n=3, cutoff=0.5)
            print(f"Close matches for '{query}': {close_matches}")
            
            # Check if it exists in other columns
            print("\nSearching in entire dataframe...")
            mask = df.astype(str).apply(lambda x: x.str.contains(query, case=False)).any(axis=1)
            other_matches = df[mask]
            if not other_matches.empty:
                print("Found match in other columns:")
                print(other_matches)
            else:
                 print("No match found in entire matching.")
                 
    else:
        print("Column 'BLKNAME' not found!")

except Exception as e:
    print(f"Error reading excel: {e}")
