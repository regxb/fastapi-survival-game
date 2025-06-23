from typing import Sequence

from fastapi import HTTPException

from app.models import Inventory, Item, Player, PlayerResources, EquipItem, BuildingCost, ItemRecipe
from app.validation.map import is_farmable_area


def validate_player(player: Player | None) -> None:
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")


def validate_player_before_unequip_item(player_equip_item: EquipItem, player: Player) -> None:
    if not player_equip_item:
        raise HTTPException(status_code=404, detail="Item not found")
    if player.inventory_slots <= len(player.inventory):
        raise HTTPException(status_code=400, detail="Inventory is full")


def does_player_have_enough_resources(
        costs: Sequence[BuildingCost] | Sequence[ItemRecipe],
        player_resources: Sequence[PlayerResources]
) -> bool:
    if not player_resources:
        return False
    player_resource_dict = {res.resource_id: res.resource_quantity for res in player_resources}
    for cost in costs:
        if player_resource_dict.get(cost.resource_id, 0) < cost.resource_quantity:
            return False
    return True


def does_player_have_empty_slot(player: Player, craft_item: Item) -> bool:
    for item in player.inventory:
        if item.item_id == craft_item.id and item.count < craft_item.max_count:
            return True
    if player.inventory_slots > len(player.inventory):
        return True
    return False


def can_player_craft_item(player: Player, item: Item) -> None:
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    # if not player.base:
    #     raise HTTPException(status_code=404, detail="Player has no base")
    # if player.map_object_id != player.base.map_object_id:
    #     raise HTTPException(status_code=400, detail="The player is not at the base")
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not does_player_have_enough_resources(item.recipe, player.resources):
        raise HTTPException(status_code=400, detail="Not enough resources")
    if not does_player_have_empty_slot(player, item):
        raise HTTPException(status_code=400, detail="Inventory is full")


def can_player_transfer_items(player: Player, direction: str) -> None:
    if not player.base:
        raise HTTPException(status_code=404, detail="Player has no base")
    if player.map_object_id != player.base.map_object_id:
        raise HTTPException(status_code=400, detail="The player is not at the base")
    if direction == "to_storage" and not player.inventory:
        raise HTTPException(status_code=404, detail="Player has no item")
    if direction == "from_storage" and not player.base.items:
        raise HTTPException(status_code=404, detail="Player has no item")


def can_player_transfer_resources(
        player: Player,
        count: int,
        direction: str,
) -> None:
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    if not player.base:
        raise HTTPException(status_code=404, detail="Player has no base")
    if player.map_object_id != player.base.map_object_id:
        raise HTTPException(status_code=404, detail="The player is not at the base")
    if direction == "to_storage":
        if not player.resources:
            raise HTTPException(status_code=400, detail="Not enough resources")
        if player.resources[0].resource_quantity < count:
            raise HTTPException(status_code=400, detail="Not enough resources")
    if direction == "from_storage":
        if not player.base.resources:
            raise HTTPException(status_code=400, detail="Not enough resources")
        if player.base.resources[0].resource_quantity < count:
            raise HTTPException(status_code=400, detail="Not enough resources")


def can_player_do_something(player: Player) -> None:
    if player.status != "waiting" and player.status != "recovery":
        raise HTTPException(status_code=400, detail="The player is currently doing some action")
    if not player or player.map_id is None:
        raise HTTPException(status_code=404, detail="Player is not on the map")


def can_player_move_to_new_map_object(player_map_object_id: int, map_object_id: int) -> None:
    if player_map_object_id == map_object_id:
        raise HTTPException(status_code=409, detail="The user is already at this place")


def validate_player_before_farming(player: Player, total_minutes: int) -> None:
    validate_player(player)
    can_player_do_something(player)
    is_farmable_area(player.map_object)
    if player.energy - total_minutes < 0:
        raise HTTPException(status_code=400, detail="Not enough energy to start farming")


def validate_inventory_item(inventory_item: Inventory) -> None:
    if not inventory_item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not inventory_item.item.can_equip:
        raise HTTPException(status_code=400, detail="Cant equip this item")
