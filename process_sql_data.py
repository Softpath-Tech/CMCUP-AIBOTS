import pandas as pd
import os

# Paths
CSV_DIR = r"c:\Users\Rishabh\Desktop\RISHABH AI LEARNING\rag-chatbot\data\csvs"
MD_DIR = r"c:\Users\Rishabh\Desktop\RISHABH AI LEARNING\rag-chatbot\data\mdFiles"

os.makedirs(MD_DIR, exist_ok=True)

def clean_text(text):
    if pd.isna(text) or text == "NULL":
        return "Unknown"
    return str(text).strip()

def process_districts():
    print("Processing Districts...")
    try:
        df = pd.read_csv(os.path.join(CSV_DIR, "districtmaster.csv"))
        lines = []
        for _, row in df.iterrows():
            line = f"District **{clean_text(row.get('DistrictName'))}** (ID: {row.get('DistrictNo')}) has Code '{clean_text(row.get('Dist_code'))}'."
            lines.append(line)
        
        with open(os.path.join(MD_DIR, "rag_districts.md"), "w", encoding="utf-8") as f:
            f.write("# District Information\n\n" + "\n".join(lines))
        print("✅ Districts Done.")
    except Exception as e:
        print(f"❌ Districts Failed: {e}")

def process_mandals():
    print("Processing Mandals...")
    try:
        df = pd.read_csv(os.path.join(CSV_DIR, "mandalmaster.csv"))
        lines = []
        for _, row in df.iterrows():
            line = f"Mandal **{clean_text(row.get('MandalName'))}** is in District ID {row.get('DistrictNo')}. It falls under Assembly Constituency **{clean_text(row.get('ac_name'))}**."
            lines.append(line)
        
        with open(os.path.join(MD_DIR, "rag_mandals.md"), "w", encoding="utf-8") as f:
            f.write("# Mandal Information\n\n" + "\n".join(lines))
        print("✅ Mandals Done.")
    except Exception as e:
        print(f"❌ Mandals Failed: {e}")

def process_villages():
    print("Processing Villages...")
    try:
        df = pd.read_csv(os.path.join(CSV_DIR, "villagemaster.csv"))
        lines = []
        # Limiting output if too huge, but RAG can handle text. For safety, let's dump all.
        for _, row in df.iterrows():
            line = f"Village **{clean_text(row.get('VillageName'))}** belongs to Mandal ID {row.get('MandalNo')} in District ID {row.get('DistNo')}."
            lines.append(line)
        
        with open(os.path.join(MD_DIR, "rag_villages.md"), "w", encoding="utf-8") as f:
            f.write("# Village Information\n\n" + "\n".join(lines))
        print("✅ Villages Done.")
    except Exception as e:
        print(f"❌ Villages Failed: {e}")

def process_clusters():
    print("Processing Clusters...")
    try:
        df = pd.read_csv(os.path.join(CSV_DIR, "clustermaster.csv"))
        lines = []
        for _, row in df.iterrows():
            line = f"Cluster **{clean_text(row.get('clustername'))}** (ID: {row.get('cluster_id')}) is in Mandal ID {row.get('mand_id')}, District ID {row.get('dist_id')}."
            lines.append(line)
        
        with open(os.path.join(MD_DIR, "rag_clusters.md"), "w", encoding="utf-8") as f:
            f.write("# Cluster Information\n\n" + "\n".join(lines))
        print("✅ Clusters Done.")
    except Exception as e:
        print(f"❌ Clusters Failed: {e}")

def process_disciplines():
    print("Processing Disciplines (Sports)...")
    try:
        df = pd.read_csv(os.path.join(CSV_DIR, "tb_discipline.csv"))
        lines = []
        for _, row in df.iterrows():
            age_range = f"{clean_text(row.get('from_age'))} to {clean_text(row.get('to_age'))}"
            line = f"Sport: **{clean_text(row.get('dist_game_nm'))}** (ID: {row.get('game_id')}). Age Eligibility: {age_range} years. Team Size: {clean_text(row.get('team_size'))} players."
            lines.append(line)
        
        with open(os.path.join(MD_DIR, "rag_disciplines.md"), "w", encoding="utf-8") as f:
            f.write("# Sports Discipline Details\n\n" + "\n".join(lines))
        print("✅ Disciplines Done.")
    except Exception as e:
        print(f"❌ Disciplines Failed: {e}")

def process_events():
    print("Processing Events...")
    try:
        df = pd.read_csv(os.path.join(CSV_DIR, "tb_events.csv"))
        lines = []
        for _, row in df.iterrows():
            line = f"Event **{clean_text(row.get('event_name'))}** belongs to Discipline ID {row.get('discipline_id')}. Category: {clean_text(row.get('cat_no'))}."
            lines.append(line)
        
        with open(os.path.join(MD_DIR, "rag_events.md"), "w", encoding="utf-8") as f:
            f.write("# Sports Event List\n\n" + "\n".join(lines))
        print("✅ Events Done.")
    except Exception as e:
        print(f"❌ Events Failed: {e}")

def process_fixtures():
    print("Processing Fixtures...")
    try:
        df = pd.read_csv(os.path.join(CSV_DIR, "tb_fixtures.csv"))
        lines = []
        for _, row in df.iterrows():
            match_name = clean_text(row.get('match_no'))
            line = f"Match **{match_name}** (Fixture ID: {row.get('fixture_id')}) is scheduled for **{clean_text(row.get('match_day'))}** at **{clean_text(row.get('match_time'))}**. Venue: {clean_text(row.get('venue'))}. Match is between District ID {row.get('team1_dist_id')} and District ID {row.get('team2_dist_id')}."
            lines.append(line)
        
        with open(os.path.join(MD_DIR, "rag_fixtures.md"), "w", encoding="utf-8") as f:
            f.write("# Tournament Fixtures / Schedule\n\n" + "\n".join(lines))
        print("✅ Fixtures Done.")
    except Exception as e:
        print(f"❌ Fixtures Failed: {e}")

if __name__ == "__main__":
    process_districts()
    process_mandals()
    process_villages()
    process_clusters()
    process_disciplines()
    process_events()
    process_fixtures()
    print("\n🎉 All CSVs processed into Markdown files for RAG!")
