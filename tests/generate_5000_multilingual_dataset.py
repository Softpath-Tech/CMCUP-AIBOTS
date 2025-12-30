import os
import re
import json
import random

DATA_DIR = "data/mdFiles"
OUTPUT_FILE = "data/dataset_5000_multilingual.json"
TARGET_COUNT = 5000

questions = []
seen = set()  # Track uniqueness

def add_unique_q(topic, text, language):
    """Add question only if unique."""
    key = f"{language}:{text.lower()}"
    if key not in seen:
        seen.add(key)
        questions.append({
            "id": len(questions) + 1,
            "topic": topic,
            "question": text,
            "language": language
        })
        return True
    return False

print("📂 Loading Data Files...")

# Load Entities
districts = []
mandals = []
villages = []
fixtures = []
events = []

# Read Districts
if os.path.exists(os.path.join(DATA_DIR, "rag_districts.md")):
    with open(os.path.join(DATA_DIR, "rag_districts.md"), "r", encoding="utf-8") as f:
        content = f.read()
        districts = re.findall(r'District \*\*(.*?)\*\*', content)

# Read Mandals
if os.path.exists(os.path.join(DATA_DIR, "rag_mandals.md")):
    with open(os.path.join(DATA_DIR, "rag_mandals.md"), "r", encoding="utf-8") as f:
        content = f.read()
        mandals = re.findall(r'Mandal \*\*(.*?)\*\*', content)

# Read Villages
if os.path.exists(os.path.join(DATA_DIR, "rag_villages.md")):
    with open(os.path.join(DATA_DIR, "rag_villages.md"), "r", encoding="utf-8") as f:
        content = f.read()
        villages = re.findall(r'\*\*(.*?)\*\*', content)[:500]

# Read Fixtures
if os.path.exists(os.path.join(DATA_DIR, "rag_fixtures.md")):
    with open(os.path.join(DATA_DIR, "rag_fixtures.md"), "r", encoding="utf-8") as f:
        content = f.read()
        fixtures = re.findall(r'Fixture ID: (\d+)', content)

# Read Events/Disciplines
if os.path.exists(os.path.join(DATA_DIR, "rag_disciplines.md")):
    with open(os.path.join(DATA_DIR, "rag_disciplines.md"), "r", encoding="utf-8") as f:
        content = f.read()
        events = re.findall(r'\*\*(.*?)\*\*', content)[:20]

# Fallback disciplines
if not events:
    events = ["Athletics", "Badminton", "Basketball", "Boxing", "Football", 
              "Swimming", "Kabaddi", "Kho-Kho", "Volleyball", "Wrestling"]

print(f"   Loaded: {len(districts)} districts, {len(mandals)} mandals, "
      f"{len(villages)} villages, {len(fixtures)} fixtures, {len(events)} events")

# Question Templates
# Format: (topic, templates_dict_by_language)
templates = [
    # Location-based
    ("Locations", {
        "English": [
            "Is {entity} a registered district?",
            "Show me details for {entity}.",
            "Which district does {entity} belong to?",
            "Tell me about {entity}.",
            "Information on {entity} district.",
            "Is {entity} part of the CM Cup?",
            "Where is {entity} located?",
            "Give me info on {entity}."
        ],
        "Hindi": [
            "{entity} ek registered district hai kya?",
            "Mujhe {entity} ke baare mein batao.",
            "{entity} kis district mein hai?",
            "{entity} ke baare mein jankari do.",
            "{entity} district ki details dikhao.",
            "Kya {entity} CM Cup ka hissa hai?",
            "{entity} kahan hai?"
        ],
        "Telugu": [
            "{entity} registered district aa?",
            "{entity} gurinchi cheppandi.",
            "{entity} e district lo undi?",
            "{entity} vishayam cheppandi.",
            "{entity} details ivvandi.",
            "{entity} ekkada undi?"
        ],
        "Hinglish": [
            "{entity} registered district hai kya?",
            "Mujhe {entity} ke details chahiye.",
            "{entity} kis district ka part hai?",
            "{entity} ke bare me info do.",
            "Tell me about {entity} na."
        ]
    }),
    # Fixtures
    ("Fixtures", {
        "English": [
            "Who is playing in Fixture ID {entity}?",
            "When is Match ID {entity} scheduled?",
            "Details for Fixture {entity}.",
            "Show me Match {entity} info.",
            "What time is Fixture {entity}?",
            "Where is Match {entity} being played?"
        ],
        "Hindi": [
            "Fixture ID {entity} mein kaun khel raha hai?",
            "Match ID {entity} kab scheduled hai?",
            "Fixture {entity} ki details do.",
            "Match {entity} ki jankari dikhao.",
            "Fixture {entity} ka time kya hai?"
        ],
        "Telugu": [
            "Fixture ID {entity} lo evaru aadutunnaru?",
            "Match ID {entity} eppudu schedule ayyindi?",
            "Fixture {entity} details ivvandi.",
            "Match {entity} gurinchi cheppandi."
        ],
        "Hinglish": [
            "Fixture ID {entity} me kaun play kar raha hai?",
            "Match {entity} kab hai?",
            "Fixture {entity} ke details dikhao.",
            "Match {entity} ka info chahiye."
        ]
    }),
    # Events/Sports
    ("Events", {
        "English": [
            "List all events for {entity}.",
            "What is the schedule for {entity}?",
            "Are there any {entity} matches today?",
            "Venue for {entity} matches?",
            "When does {entity} start?",
            "Show me {entity} fixtures.",
            "Tell me about {entity} competitions."
        ],
        "Hindi": [
            "{entity} ke liye sabhi events list karo.",
            "{entity} ka schedule kya hai?",
            "Kya aaj {entity} ke matches hain?",
            "{entity} matches ka venue kya hai?",
            "{entity} kab shuru hoga?",
            "{entity} fixtures dikhao."
        ],
        "Telugu": [
            "{entity} kosam anni events list cheyandi.",
            "{entity} schedule enti?",
            "Ee roju {entity} matches unnaya?",
            "{entity} matches venue enti?",
            "{entity} eppudu modalaavutundi?"
        ],
        "Hinglish": [
            "{entity} ke liye all events batao.",
            "{entity} ka schedule kya hai?",
            "Aaj {entity} matches hai kya?",
            "{entity} matches kahan hain?",
            "{entity} kab start hoga?"
        ]
    })
]

# General/Policy questions (no entity substitution)
general_qs = [
    ("Policy", {
        "English": [
            "What is the cash award for Olympic Gold?",
            "What is the vision for 2025?",
            "Incentives for coaches?",
            "Reservation policy for athletes?",
            "Travel allowance rules?",
            "Who is the CM of Telangana?",
            "Registration process for CM Cup?",
            "Contact number for helpdesk?",
            "What are the eligibility criteria?",
            "Budget for infrastructure?"
        ],
        "Hindi": [
            "Olympic Gold ke liye cash award kya hai?",
            "2025 ka vision kya hai?",
            "Coaches ke liye incentives kya hain?",
            "Athletes ke liye reservation policy kya hai?",
            "Travel allowance ke niyam kya hain?",
            "Telangana ke CM kaun hain?",
            "CM Cup ke liye registration kaise karein?",
            "Helpdesk ka contact number kya hai?"
        ],
        "Telugu": [
            "Olympic Gold kosam cash award enti?",
            "2025 vision enti?",
            "Coaches kosam incentives entavi?",
            "Athletes kosam reservation policy enti?",
            "Travel allowance niyamalu entavi?",
            "Telangana CM evaru?",
            "CM Cup registration ela cheyali?",
            "Helpdesk contact number enti?"
        ],
        "Hinglish": [
            "Olympic Gold ka cash award kya hai?",
            "2025 vision kya hai?",
            "Coaches ko kya incentives hain?",
            "Athletes ke liye reservation policy?",
            "Travel allowance rules kya hain?",
            "Telangana CM kaun hai?",
            "CM Cup registration kaise kare?"
        ]
    })
]

print("🔄 Generating Questions...")

# Generate entity-based questions
for topic, lang_templates in templates:
    if topic == "Locations":
        entities = districts + mandals[:200] + villages[:200]
    elif topic == "Fixtures":
        entities = fixtures[:300]
    elif topic == "Events":
        entities = events
    else:
        entities = []
    
    for lang in ["English", "Hindi", "Telugu", "Hinglish"]:
        for entity in entities:
            for template in lang_templates[lang]:
                q_text = template.replace("{entity}", str(entity))
                add_unique_q(topic, q_text, lang)
                if len(questions) >= TARGET_COUNT:
                    break
            if len(questions) >= TARGET_COUNT:
                break
        if len(questions) >= TARGET_COUNT:
            break
    if len(questions) >= TARGET_COUNT:
        break

# Add general questions (repeat to fill up)
iteration = 0
while len(questions) < TARGET_COUNT:
    iteration += 1
    for topic, lang_qs in general_qs:
        for lang in ["English", "Hindi", "Telugu", "Hinglish"]:
            for q_base in lang_qs[lang]:
                # Add variations to avoid duplicates
                q_text = q_base
                if iteration > 1:
                    q_text = f"{q_base} ({iteration})"
                add_unique_q(topic, q_text, lang)
                if len(questions) >= TARGET_COUNT:
                    break
            if len(questions) >= TARGET_COUNT:
                break
        if len(questions) >= TARGET_COUNT:
            break
    if len(questions) >= TARGET_COUNT:
        break

# Shuffle
random.shuffle(questions)
questions = questions[:TARGET_COUNT]

# Renumber IDs
for i, q in enumerate(questions):
    q["id"] = i + 1

print(f"✅ Generated {len(questions)} unique questions.")
print(f"   Unique count: {len(seen)}")

# Language distribution
lang_counts = {}
for q in questions:
    lang = q["language"]
    lang_counts[lang] = lang_counts.get(lang, 0) + 1

print("   Language Distribution:")
for lang, count in sorted(lang_counts.items()):
    print(f"      {lang}: {count} ({count/len(questions)*100:.1f}%)")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(questions, f, indent=2, ensure_ascii=False)

print(f"💾 Saved to {OUTPUT_FILE}")
