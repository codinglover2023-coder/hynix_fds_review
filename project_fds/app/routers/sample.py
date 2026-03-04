from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/sample", tags=["sample"])

# 인메모리 저장소
_store: dict[int, dict] = {}
_seq = 0


class SampleCreate(BaseModel):
    name: str
    description: str = ""


class SampleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


@router.get("/")
async def list_items():
    return list(_store.values())


@router.get("/{item_id}")
async def get_item(item_id: int):
    if item_id not in _store:
        raise HTTPException(status_code=404, detail="Item not found")
    return _store[item_id]


@router.post("/", status_code=201)
async def create_item(body: SampleCreate):
    global _seq
    _seq += 1
    item = {"id": _seq, "name": body.name, "description": body.description}
    _store[_seq] = item
    return item


@router.put("/{item_id}")
async def update_item(item_id: int, body: SampleUpdate):
    if item_id not in _store:
        raise HTTPException(status_code=404, detail="Item not found")
    item = _store[item_id]
    if body.name is not None:
        item["name"] = body.name
    if body.description is not None:
        item["description"] = body.description
    return item


@router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: int):
    if item_id not in _store:
        raise HTTPException(status_code=404, detail="Item not found")
    del _store[item_id]
