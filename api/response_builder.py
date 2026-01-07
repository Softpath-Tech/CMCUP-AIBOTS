# response_builder.py

from models import ChatResponse, MenuItem
from menu_index import MAIN_MENUS


def build_response(
    text: str,
    menus: list | None,
    source: str,
    session_id: str
):
    menu_items = [MenuItem(**m) for m in menus] if menus else []

    return ChatResponse(
        text=text,
        menus=menu_items,
        isMenusAvailable=bool(menu_items),
        source=source,
        session_id=session_id
    )


def welcome_response(session_id: str):
    return build_response(
        text=(
            "🏆 **Welcome to Telangana Sports Authority – CM Cup 2025 Chatbot** 👋\n\n"
            "I can help players, parents, coaches, and officials."
        ),
        menus=MAIN_MENUS,
        source="menu_system",
        session_id=session_id
    )
