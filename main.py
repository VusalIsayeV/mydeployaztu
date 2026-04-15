from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
import os

app = FastAPI(
    title="Portfolio API - Deploy Test ✅ (Vusal)",
    description="FastAPI CRUD with fake JSON database",
    version="1.0.0",
)

DB_FILE = os.path.join(os.path.dirname(__file__), "db.json")


def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"items": [], "next_id": 1}, f)
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class ItemIn(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


class Item(ItemIn):
    id: int


@app.get("/", tags=["root"])
def root():
    return {"message": "Portfolio API işləyir", "docs": "/docs"}


@app.get("/items", response_model=list[Item], tags=["items"])
def list_items():
    return load_db()["items"]


@app.get("/items/{item_id}", response_model=Item, tags=["items"])
def get_item(item_id: int):
    db = load_db()
    for item in db["items"]:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item tapılmadı")


@app.post("/items", response_model=Item, status_code=201, tags=["items"])
def create_item(payload: ItemIn):
    db = load_db()
    new_item = {"id": db["next_id"], **payload.model_dump()}
    db["items"].append(new_item)
    db["next_id"] += 1
    save_db(db)
    return new_item


@app.put("/items/{item_id}", response_model=Item, tags=["items"])
def update_item(item_id: int, payload: ItemIn):
    db = load_db()
    for idx, item in enumerate(db["items"]):
        if item["id"] == item_id:
            updated = {"id": item_id, **payload.model_dump()}
            db["items"][idx] = updated
            save_db(db)
            return updated
    raise HTTPException(status_code=404, detail="Item tapılmadı")


@app.delete("/items/{item_id}", tags=["items"])
def delete_item(item_id: int):
    db = load_db()
    for idx, item in enumerate(db["items"]):
        if item["id"] == item_id:
            db["items"].pop(idx)
            save_db(db)
            return {"ok": True, "deleted_id": item_id}
    raise HTTPException(status_code=404, detail="Item tapılmadı")
