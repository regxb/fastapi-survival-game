from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Player, Item, ItemRecipe, Inventory
from app.repository import player_repository, item_repository
from app.schemas import ItemResponseSchema, RecipeSchema, ResourceCountSchema, CraftItemSchema, ItemSchemaResponse
from app.services.validation import ValidationService
from app.services.base import BaseService
from app.services.player import PlayerResponseService, PlayerService


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
                    resources=[ResourceCountSchema(id=recipe.resource.id, name=recipe.resource.name, count=recipe.resource_quantity, icon=recipe.resource.icon) for recipe in item.recipe]
                ),
            )
            for item in items
        ]

        return response

    async def craft(self, telegram_id: int, craft_data: CraftItemSchema) -> list[ItemSchemaResponse]:
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

        player_inventory = Inventory(player_id=player.id, item_id=item.id)
        self.session.add(player_inventory)
        await BaseService.commit_or_rollback(self.session)
        await self.session.refresh(player)

        return PlayerResponseService.serialize_inventory(player.inventory)
