from typing import Optional, Sequence

from app.models import Item, Player
from app.schemas import (ItemResponseSchema, ItemSchema, PlayerItemsSchema, RecipeSchema, ResourceCountSchema,
                         )
from app.validation.player import does_player_have_enough_resources


def serialize_item_recipe(items: Sequence[Item], player: Player) -> list[ItemResponseSchema]:
    response = [
        ItemResponseSchema(
            id=item.id,
            name=item.name,
            can_craft=does_player_have_enough_resources(item.recipe, player.resources),
            icon=item.icon,
            recipe=RecipeSchema(
                resources=[
                    ResourceCountSchema(
                        id=recipe.resource.id,
                        name=recipe.resource.name,
                        count=recipe.resource_quantity,
                        icon=recipe.resource.icon
                    ) for recipe in item.recipe
                ]
            ),
        )
        for item in items
    ]

    return response


def serialize_items(items: Sequence) -> Optional[list[ItemSchema]]:
    items = [
        ItemSchema(
            id=item.id,
            name=item.item.name,
            tier=item.tier,
            icon=item.item.icon,
            type=item.item.type,
            count=item.count,
            damage=item.item.stats.damage,
            armor=item.item.stats.armor,
        )
        for item in items]
    return items or None


def serialize_equip_items(items: Sequence) -> Optional[list[ItemSchema]]:
    items = [
        ItemSchema(
            id=item.id,
            name=item.item.name,
            tier=item.tier,
            icon=item.item.icon,
            type=item.item.type,
            damage=item.item.stats.damage,
            armor=item.item.stats.armor,
        )
        for item in items]
    return items or None


def serialize_player_items(player: Player) -> PlayerItemsSchema:
    storage_items = serialize_items(player.base.items)
    inventory_items = serialize_items(player.inventory)
    equip_items = serialize_equip_items(player.equip_item)
    return PlayerItemsSchema(storage_items=storage_items, inventory_items=inventory_items, equip_items=equip_items)
