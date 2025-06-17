from abc import ABC, abstractmethod
from typing import Optional, Union

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Inventory, Item, ItemRecipe, Player, PlayerBase, PlayerItemStorage
from app.repository import item_repository, player_repository, inventory_repository, player_item_storage_repository
from app.schemas import (CraftItemSchema, ItemResponseSchema,
                         ItemSchemaResponse, RecipeSchema, ResourceCountSchema, TransferItemSchema,
                         PlayerItemsSchema, StorageItemCreateSchema, InventoryItemCreateSchema, EquipItemSchema,
                         ItemLocation)
from app.services.base import BaseService, BaseTransferService
from app.services.player import PlayerResponseService, PlayerService
from app.services.validation import ValidationService


class ItemContainer(ABC):
    def __init__(self, player: Player):
        self.player = player

    @abstractmethod
    def get_item(self) -> list:
        pass

    @abstractmethod
    async def create_item(self, session: AsyncSession, item: Item, count: int) -> None:
        pass


class StorageContainer(ItemContainer):
    def get_item(self) -> list:
        return self.player.base.items

    async def create_item(self, session: AsyncSession, item: Item, count: int) -> None:
        schema = StorageItemCreateSchema(player_base_id=self.player.base.id, **item.__dict__)
        schema.count = count
        await player_item_storage_repository.create(session, schema)


class InventoryContainer(ItemContainer):
    def get_item(self) -> list:
        return self.player.inventory

    async def create_item(self, session: AsyncSession, item: Item, count: int) -> None:
        schema = InventoryItemCreateSchema(**item.__dict__)
        schema.count = count
        await inventory_repository.create(session, schema)


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

    async def delete(self, telegram_id: int, map_id: int, item_id: int, item_location: ItemLocation):
        player = await player_repository.get(
            self.session,
            options=[joinedload(Player.inventory).joinedload(Inventory.item).joinedload(Item.type)],
            player_id=telegram_id,
            map_id=map_id
        )
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        if item_location.value == "inventory":
            item = await inventory_repository.get(self.session, id=item_id, player_id=player.id)
        elif item_location.value == "storage":
            item = await player_item_storage_repository.get(self.session, id=item_id, player_id=player.id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        await self.session.delete(item)
        await BaseService.commit_or_rollback(self.session)
        return PlayerResponseService.serialize_inventory(player.inventory)

    async def craft(self, telegram_id: int, craft_data: CraftItemSchema) -> list[ItemSchemaResponse] | None:
        player = await player_repository.get(
            self.session,
            options=[
                joinedload(Player.resources),
                joinedload(Player.base).joinedload(PlayerBase.items),
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

        self._update_inventory_items(player, item)

        await BaseService.commit_or_rollback(self.session)
        await self.session.refresh(player)

        return PlayerResponseService.serialize_inventory(player.inventory)

    def _update_inventory_items(self, player: Player, item: Item):
        player.inventory.sort(key=lambda i: i.count)

        if not player.inventory or not any(inv.item == item for inv in player.inventory):
            player_inventory = Inventory(player_id=player.id, item_id=item.id)
            self.session.add(player_inventory)
        else:
            for items in player.inventory:
                if items.item_id == item.id and items.count < item.max_count:
                    items.count += 1
                    return
            player_inventory = Inventory(player_id=player.id, item_id=item.id)
            self.session.add(player_inventory)


class ItemTransferService(BaseTransferService):
    async def transfer(self, telegram_id: int, transfer_data: TransferItemSchema) -> PlayerItemsSchema:
        player = await self._get_player_with_items(telegram_id, transfer_data.map_id)
        self._validate_transfer(player, transfer_data.direction.value)
        await self._update_items(player, transfer_data.item_id, transfer_data.direction.value, transfer_data.count)
        await BaseService.commit_or_rollback(self.session)
        await self.session.refresh(player)
        return await self._serialize_player_items(player)

    async def _get_player_with_items(self, telegram_id: int, map_id: int) -> Player:
        player = await player_repository.get(
            self.session,
            options=[
                joinedload(Player.inventory).joinedload(Inventory.item),
                joinedload(Player.base).joinedload(PlayerBase.items).joinedload(PlayerItemStorage.item),
            ],
            player_id=telegram_id,
            map_id=map_id
        )
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        return player

    def _validate_transfer(self, player: Player, direction: str) -> None:
        ValidationService.can_player_transfer_items(player, direction)

    async def _update_items(self, player: Player, item_id: int, direction: str, count: int) -> None:
        if direction == "to_storage":
            await self._move_item_to_storage(player, item_id, count)
        elif direction == "from_storage":
            await self._move_item_from_storage(player, item_id, count)

    async def _move_item(self, source_item: Item, count: int, target_container: ItemContainer):
        max_count = source_item.item.max_count
        existing_item = next(
            (inv for inv in target_container.get_item() if
             inv.item_id == source_item.item_id and inv.count < max_count), None
        )
        if existing_item:
            available_space = max_count - existing_item.count
            if count <= available_space:
                existing_item.count += count
            else:
                existing_item.count = max_count
                await target_container.create_item(self.session, source_item, count - available_space)
        else:
            await target_container.create_item(self.session, source_item, count)

        if source_item.count <= count:
            await self.session.delete(source_item)
        else:
            source_item.count -= count

        await BaseService.commit_or_rollback(self.session)

    async def _move_item_to_storage(self, player: Player, item_id: int, count: int) -> None:
        item = await inventory_repository.get(self.session, id=item_id, player_id=player.id)
        self._validate_item(item, player.id, count)
        container = StorageContainer(player)
        await self._move_item(item, count, container)

    async def _move_item_from_storage(self, player: Player, item_id: int, count: int) -> None:
        item = await player_item_storage_repository.get(self.session, id=item_id, player_id=player.id)
        self._validate_item(item, player.id, count)
        container = InventoryContainer(player)
        await self._move_item(item, count, container)

    def _validate_item(self, item: Optional[Union[Inventory, PlayerItemStorage]], player_id: int, count: int) -> None:
        if not item or item.player_id != player_id:
            raise HTTPException(status_code=404, detail="Item not found")
        if count > item.count:
            raise HTTPException(status_code=404, detail="Player not have enough items")

    async def _serialize_player_items(self, player: Player) -> PlayerItemsSchema:
        storage_items = PlayerResponseService.serialize_storage_items(player.base.items)
        inventory_items = PlayerResponseService.serialize_inventory(player.inventory)
        return PlayerItemsSchema(storage_items=storage_items, inventory_items=inventory_items)


class ItemEquipService(BaseService):

    async def equip(self, telegram_id: int, equip_data: EquipItemSchema):
        player = await player_repository.get(
            self.session,
            options=[joinedload(Player.inventory).joinedload(Inventory.item)],
            player_id=telegram_id,
            map_id=equip_data.map_id
        )
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        player_item = await inventory_repository.get(self.session, id=equip_data.item_id, player_id=player.id)
        self._validate_equip(player_item, player)
        player_item.active = False if player_item.active else True
        await BaseService.commit_or_rollback(self.session)
        return PlayerResponseService.serialize_inventory(player.inventory)

    def _validate_equip(self, player_item: Inventory, player: Player):
        if not player_item:
            raise HTTPException(status_code=404, detail="Item not found")
        if next((inv_item for inv_item in player.inventory if self._is_matching_item(inv_item, player_item)), None):
            raise HTTPException(status_code=409, detail="Player has already taken this slot")

    def _is_matching_item(self, inv_item: Inventory, player_item: Inventory):
        return inv_item.active and not player_item.active and inv_item.item_id == player_item.item_id
