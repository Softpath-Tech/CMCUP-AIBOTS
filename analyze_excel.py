import pandas as pd
import os

file_path = "data/new data/MANDAL LEVEL CLUSTER INCHARGE NAME & PH.NO.xlsx"

try:
    # Load raw
    df = pd.read_excel(file_path, header=None)
    
    # Header is at Row 4 (Index 4). Data starts Row 5.
    start_row = 5
        
    output_text = "CM Cup 2025 Mandal Level Cluster Incharge Details:\n\n"
    count = 0
    
    current_mandal = "N/A"
    
    for i in range(start_row, len(df)):
        row = df.iloc[i]
        try:
            # Col 1: Mandal
            m_val = row[1]
            if pd.notna(m_val) and str(m_val).strip().lower() != 'nan':
                 current_mandal = str(m_val).strip()
            
            # Col 4: Cluster
            cluster = row[4]
            # Col 5: Incharge + Venue?
            incharge_raw = row[5]
            # Col 6: Contact
            contact = row[6]
            
            # Skip empty clusters
            if pd.isna(cluster) or str(cluster).strip().lower() == 'nan': continue
            
            # Format Sentence
            line = f"Mandal: {current_mandal} | Cluster: {cluster} | Incharge Details: {incharge_raw} | Contact: {contact}"
            
            # Additional cleanup
            line = line.replace("nan", "N/A").replace("  ", " ")
            output_text += line + "\n"
            count += 1
            
        except Exception as e:
            pass

    # Save
    output_path = "data/new data/Mandal_Incharges_Cleaned.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output_text)
        
    print(f"\n✅ Converted {count} rows. Saved to: {output_path}")
    print("Sample:\n" + output_text[:300])

except Exception as e:
    print(f"Error: {e}")
