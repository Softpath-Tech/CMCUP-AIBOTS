import pandas as pd

file_path = r"C:\Users\Rishabh\Desktop\RISHABH AI LEARNING\rag-chatbot\data\new data\MEO_Details.xlsx"
try:
    df = pd.read_excel(file_path)
    print("Columns:", df.columns.tolist())
    print("First 3 rows:")
    print(df.head(3).to_string())
except Exception as e:
    print(f"Error reading file: {e}")
