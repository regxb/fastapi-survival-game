from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Inventory, Item, ItemRecipe, Player
from app.repository import item_repository, player_repository
from app.schemas import (CraftItemSchema, ItemResponseSchema,
                         ItemSchemaResponse, RecipeSchema, ResourceCountSchema)
from app.services.base import BaseService
from app.services.player import PlayerResponseService, PlayerService
from app.services.validation import ValidationService


class ItemService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_items(self, map_id: int, telegram_id: int) -> list[ItemResponseSchema]:
        player = await player_repository.get(
            self.session,
            options=[
                joinedload(Player.base),
                joinedload(Player.resources),
            ],
            player_id=telegram_id,
            map_id=map_id
        )
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        items = await item_repository.get_multi(
            self.session,
            options=[joinedload(Item.recipe).joinedload(ItemRecipe.resource)],
        )

        response = [
            ItemResponseSchema(
                id=item.id,
                name=item.name,
                can_craft=ValidationService.does_user_have_enough_resources(item.recipe, player.resources),
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

    async def add(self, player, item_id: int, count: int = 1):
        existing_item = next((inv for inv in player.inventory if inv.item_id == item_id), None)

        if existing_item:
            existing_item.count += count
        else:
            new_inventory_item = Inventory(player_id=player.id, item_id=item_id, count=count)
            self.session.add(new_inventory_item)

    async def craft(self, telegram_id: int, craft_data: CraftItemSchema) -> list[ItemSchemaResponse] | None:
        player = await player_repository.get(
            self.session,
            options=[
                joinedload(Player.resources),
                joinedload(Player.base),
                joinedload(Player.inventory).joinedload(Inventory.item)
            ],
            player_id=telegram_id,
            map_id=craft_data.map_id
        )

        item = await item_repository.get(
            self.session,
            options=[joinedload(Item.recipe).joinedload(ItemRecipe.resource)],
            id=craft_data.item_id
        )

        ValidationService.can_player_craft_item(player, item)

        for recipe in item.recipe:
            PlayerService.update_resources(
                player.resources, recipe.resource_id, recipe.resource_quantity, "decrease"
            )

        await self.add(player, item.id)

        await BaseService.commit_or_rollback(self.session)
        await self.session.refresh(player)

        return PlayerResponseService.serialize_inventory(player.inventory)

