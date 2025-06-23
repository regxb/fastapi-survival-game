from typing import Optional

from app.models import Player, PlayerBase
from app.schemas import PlayerBaseSchema, PlayerResourcesSchema, PlayerSchema
from app.serialization.farm import serialize_farm_session
from app.serialization.item import serialize_items, serialize_equip_items
from app.serialization.resource import serialize_resources


def serialize_base(base: PlayerBase) -> Optional[PlayerBaseSchema]:
    if not base:
        return None

    resources = serialize_resources(base.resources)
    items = serialize_items(base.items)
    return PlayerBaseSchema(map_object_id=base.map_object_id, items=items, resources=resources)


def player_serialize(player, farm_session) -> PlayerSchema:
    farm_session_schema = serialize_farm_session(farm_session)
    in_base = player.map_object_id == player.base.map_object_id if player.base else False
    resources = serialize_resources(player.resources)
    base = serialize_base(player.base)
    inventory_items = serialize_items(player.inventory)
    equip_items = serialize_equip_items(player.equip_item)
    player_data = {key: value for key, value in player.__dict__.items()
                   if key not in ["base", "resources", "inventory"]}

    return PlayerSchema(
        in_base=in_base,
        base=base,
        farm_sessions=farm_session_schema,
        resources=resources,
        inventory_items=inventory_items,
        equip_items=equip_items,
        **player_data
    )


def serialize_player_resources(player: Player) -> PlayerResourcesSchema:
    player_resources = serialize_resources(player.resources)
    storage_resources = serialize_resources(player.base.resources)
    response = PlayerResourcesSchema(player_resources=player_resources, storage_resources=storage_resources)
    return response
