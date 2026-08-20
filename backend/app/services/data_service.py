import json
from pathlib import Path

from app.models.cart import Cart


DATA_FILE = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "stale_carts.json"
)


def load_carts() -> list[Cart]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return [Cart.model_validate(item) for item in data]