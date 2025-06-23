from typing import Optional, Union

from fastapi import HTTPException

from app.models import Inventory, Item, PlayerItemStorage


def validate_item_before_transfer(item: Optional[Union[Inventory, PlayerItemStorage]], player_id: int, count: int) -> None:
    if not item or item.player_id != player_id:
        raise HTTPException(status_code=404, detail="Item not found")
    if count > item.count:
        raise HTTPException(status_code=404, detail="Player not have enough items")

def validate_item(item: Item):
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

def validate_item_before_delete(item: Inventory, count: int):
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if count > item.count:
        raise HTTPException(status_code=404, detail="Not enough items")