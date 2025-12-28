import pandas as pd
import glob
import os

def print_schemas():
    files = glob.glob("data/csvs/*.csv")
    for f in files:
        df = pd.read_csv(f, dtype=str, nrows=0) # Read only headers
        print(f"\n--- {os.path.basename(f)} ---")
        for col in df.columns:
            print(f"  - {col}")

if __name__ == "__main__":
    print_schemas()
