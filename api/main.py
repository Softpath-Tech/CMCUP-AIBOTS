from fastapi import FastAPI
from uuid import uuid4
from api.menu_data import MENU_TREE
from api.menu_resolver import resolve_menu
from api.schemas import ChatResponse, MenuItem, ChatRequest

app = FastAPI()

def process_query(query: str, session_id: str = None) -> ChatResponse:
    if not session_id:
        session_id = str(uuid4())
        
    menu_key = resolve_menu(query)

    # MAIN MENU (Greetings or Start)
    if not query or query.lower() in ["hi", "hello", "start", "menu"]:
        return ChatResponse(
            text="🏆 **Welcome to Telangana Sports Authority – CM Cup 2025 Chatbot** 👋\n\nI can help players, parents, coaches, and officials.",
            menus=[
                MenuItem(name=v["name"], value=k)
                for k, v in MENU_TREE.items()
            ],
            isMenusAvailable=True,
            source="menu_system",
            session_id=session_id
        )

    # SUB-MENU NAVIGATION
    if menu_key:
        parts = menu_key.split(".")
        # If it's a major category (e.g., "1"), show sub-menu items
        if len(parts) == 1 and menu_key in MENU_TREE:
            children = MENU_TREE[menu_key]["children"]
            return ChatResponse(
                text=f"📌 **{MENU_TREE[menu_key]['name']}**",
                menus=[
                    MenuItem(name=name, value=key)
                    for key, name in children.items()
                ],
                isMenusAvailable=True,
                source="menu_system",
                session_id=session_id
            )

        # If it's a sub-menu item (e.g., "1.1"), trigger RAG (or specific logic)
        return ChatResponse(
            text=f"📄 You selected **{menu_key}**. Fetching details from knowledge base...",
            menus=[],
            isMenusAvailable=False,
            source="rag_system",
            session_id=session_id
        )

    # FALLBACK → RAG (General NL Query)
    return ChatResponse(
        text="🤖 I will search the CM Cup knowledge base and get back to you.",
        menus=[],
        isMenusAvailable=False,
        source="rag_system",
        session_id=session_id
    )

@app.get("/chat", response_model=ChatResponse)
def get_chat(query: str, session_id: str = None):
    return process_query(query, session_id)

@app.post("/ask", response_model=ChatResponse)
def post_ask(request: ChatRequest):
    return process_query(request.message, request.session_id)
