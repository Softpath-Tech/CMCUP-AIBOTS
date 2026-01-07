# intent_resolver.py

from sentence_transformers import SentenceTransformer, util
from menu_index import MENU_METADATA

model = SentenceTransformer("all-MiniLM-L6-v2")

MENU_EMBEDDINGS = [
    model.encode(
        m["title"] + " " + " ".join(m["keywords"]),
        normalize_embeddings=True
    )
    for m in MENU_METADATA
]


def resolve_menu(user_text: str, threshold: float = 0.55):
    query_emb = model.encode(user_text, normalize_embeddings=True)

    best_score = 0
    best_menu = None

    for idx, emb in enumerate(MENU_EMBEDDINGS):
        score = util.cos_sim(query_emb, emb).item()
        if score > best_score:
            best_score = score
            best_menu = MENU_METADATA[idx]

    return best_menu if best_score >= threshold else None
