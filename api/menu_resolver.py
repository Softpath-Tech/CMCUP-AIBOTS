import re
from rapidfuzz import process
from api.menu_data import MENU_TREE

def resolve_menu(user_input: str):
    user_input = user_input.lower().strip()

    # 1️⃣ Exact numeric match (1, 1.1, 2.3 etc)
    if re.fullmatch(r"\d+(\.\d+)*", user_input):
        return user_input

    # 2️⃣ Keyword fuzzy match
    all_labels = {}
    for k, v in MENU_TREE.items():
        all_labels[v["name"].lower()] = k
        for ck, cv in v["children"].items():
            all_labels[cv.lower()] = ck

    match, score, _ = process.extractOne(user_input, all_labels.keys())
    if score > 70:
        return all_labels[match]

    return None
