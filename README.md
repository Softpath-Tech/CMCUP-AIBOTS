Here is the comprehensive and professional README.md tailored exactly to your project context.Since you have a Git Merge Conflict, you should:Open README.md in VS Code.Delete everything inside it.Paste the content below.Save, Commit, and Push.🤖 CMCUP-AIBOTS: RAG Knowledge Base GeneratorThis repository contains the data processing pipeline for the CM Cup AI Chatbot.Its primary purpose is to transform raw structured data (CSV snapshots) into context-rich natural language text. These generated text files serve as the "Knowledge Base" for a Retrieval-Augmented Generation (RAG) system, allowing the AI to answer complex queries about the tournament's schedule, geography, and officials.⚠️ Important Data Architecture Note:No Direct SQL Connection: This repository does not connect to the live SQL database.External Extraction: The data extraction (SQL → CSV) is performed in a separate local environment/folder.Input Method: This project accepts the exported CSV files in the data/ directory as its source of truth.📂 Repository StructureThe project is organized to separate raw inputs from processed outputs.PlaintextCMCUP-AIBOTS/
│
├── data/                       # [INPUT] Raw CSV Snapshots (Exported from SQL)
│   ├── districtmaster.csv      # District names & IDs (e.g., Adilabad, Nirmal)
│   ├── mandalmaster.csv        # Administrative hierarchy (Mandals linked to Districts)
│   ├── clustermaster.csv       # Cluster details & Incharge Officer contacts
│   ├── villagemaster.csv       # Village level data
│   ├── tb_fixtures.csv         # Match schedules, venues, timings, and results
│   ├── tb_events.csv           # Sports event definitions (Kabaddi, Kho-Kho, etc.)
│   └── tb_discipline.csv       # Sports discipline metadata & icons
│
├── rag_knowledge_base/         # [OUTPUT] AI-Ready Text Files (Generated)
│   ├── rag_fixtures.txt        # "Narrative" style match schedules
│   ├── rag_locations.txt       # Geographical hierarchy sentences
│   └── rag_contacts.txt        # Official contact & cluster management details
│
├── process_sql_data.py         # Main ETL Script (Clean -> Join -> Generate)
├── requirements.txt            # Python dependencies
└── README.md                   # Project Documentation
⚙️ The Processing PipelineThe process_sql_data.py script acts as the bridge between raw data and the AI model. It performs three critical steps:1. Data Cleaning & StandardizationFilename Correction: Automatically detects and handles typos (e.g., dustermaster.csv vs clustermaster.csv).Header Normalization: Converts inconsistent headers (e.g., " District Name ") to a standard format (district_name).Null Handling: Intelligently manages missing data (e.g., NULL, nan) to ensure the AI doesn't generate broken sentences like "Match at nan venue".2. Denormalization (The "Join" Phase)Raw database tables use numerical IDs (e.g., TeamID: 4). The script creates lookup maps to replace these with human-readable names.Before: Match 1: Team 12 vs Team 14After: Match 1: Adilabad vs Mahabubnagar3. Natural Language Generation (NLG)The final step converts the processed rows into semantic sentences optimized for Vector Search (Embeddings).Output FileContent DescriptionExample AI-Ready Outputrag_fixtures.txtMatch Schedules`MATCH: Kabaddirag_locations.txtGeographyLOCATION: Bela is a Mandal located within Adilabad District.rag_contacts.txtOfficialsCONTACT: The Echoda Cluster in Adilabad District is managed by Incharge Officer Ravi Kumar.🛠️ Setup & Usage1. PrerequisitesPython 3.10+Git2. InstallationBashgit clone https://github.com/Softpath-Tech/CMCUP-AIBOTS.git
cd CMCUP-AIBOTS

# Create Virtual Environment (Recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install Dependencies
pip install pandas
3. Updating the Knowledge BaseWhen new data is available from the SQL database:Export the SQL tables to CSV format locally.Paste the CSV files into the data/ folder (overwrite old files).Run the processing script:Bashpython process_sql_data.py
Verify the text files in rag_knowledge_base/ are updated.📊 Dataset DictionaryTB_Fixtures: The core schedule containing Match Dates, Times, Venues (if assigned), and Team pairings.District/Mandal/Village Master: Defines the geographical hierarchy of Telangana for the tournament.Cluster Master: Groups mandals into operational clusters and assigns Incharge officers.TB_Events / Discipline: Metadata describing specific sporting events (Category, Gender, Age Group).🤝 Contribution GuidelinesDo not edit the .txt files manually. They are auto-generated.If you need to change the phrasing of the AI's knowledge, modify the generate_text functions inside process_sql_data.py.