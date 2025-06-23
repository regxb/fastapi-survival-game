from abc import ABC, abstractmethod

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Inventory, Item, Player, PlayerItemStorage, EquipItem, ItemStat
from app.repository import (create_inventory_item, create_player_inventory,
                            create_storage_item, get_player_inventory,
                            get_item_for_craft, get_items_for_craft,
                            get_player_with_items,
                            get_player_with_resources_for_craft,
                            inventory_repository,
                            player_item_storage_repository, get_inventory_item_with_stats, get_player_with_stats,
                            get_equip_item_with_specific_type, create_equip_item,
                            get_player_with_all_items, equip_item_repository, get_player_with_inventory_items)
from app.schemas import (CraftItemSchema, EquipItemSchema, ItemLocation,
                         ItemResponseSchema, PlayerItemsSchema, TransferItemSchema, PlayerEquipItemResponseSchema,
                         ItemSchema)
from app.serialization.item import (serialize_items, serialize_item_recipe,
                                    serialize_player_items)
from app.services.base import BaseService, BaseTransferService
from app.services.player import PlayerService
from app.validation.item import (validate_item_before_delete,
                                 validate_item_before_transfer)
from app.validation.player import (can_player_craft_item,
                                   can_player_transfer_items,
                                   validate_player, validate_inventory_item, validate_player_before_unequip_item)


class ItemContainer(ABC):
    def __init__(self, player: Player) -> None:
        self.player = player

    @abstractmethod
    def get_item(self) -> list:
        pass

    @abstractmethod
    async def create_item(self, session: AsyncSession, item: PlayerItemStorage | Inventory, count: int) -> None:
        pass


class StorageContainer(ItemContainer):
    def get_item(self) -> list:
        return self.player.base.items

    async def create_item(self, session: AsyncSession, item: PlayerItemStorage, count: int) -> None:
        create_storage_item(session, item.item_id, count, self.player.base.id, self.player.id, item.tier)


class InventoryContainer(ItemContainer):
    def get_item(self) -> list:
        return self.player.inventory

    async def create_item(self, session: AsyncSession, item: Inventory, count: int) -> None:
        create_inventory_item(session, item.item_id, self.player.id, count, item.tier)


class ItemService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_items(self, map_id: int, telegram_id: int) -> list[ItemResponseSchema]:
        player = await get_player_with_resources_for_craft(self.session, telegram_id, map_id)
        items = await get_items_for_craft(self.session)
        response = serialize_item_recipe(items, player)
        return response

    async def delete(
            self,
            telegram_id: int,
            map_id: int,
            item_id: int,
            count: int,
            item_location: ItemLocation
    ) -> PlayerItemsSchema:
        player = await get_player_with_items(self.session, telegram_id, map_id)
        validate_player(player)
        player_id = player.id
        if item_location.value == "inventory":
            repository = inventory_repository
        elif item_location.value == "storage":
            repository = player_item_storage_repository
        else:
            raise HTTPException(status_code=404, detail="Direction not found")
        item = await repository.get(self.session, id=item_id, player_id=player.id)
        validate_item_before_delete(item, count)

        await self.update_item_after_delete(item, count)
        await BaseService.commit_or_rollback(self.session)
        player = await get_player_with_all_items(self.session, player_id)
        return serialize_player_items(player)

    async def update_item_after_delete(self, item: Inventory, count: int) -> None:
        if item.count == count:
            await self.session.delete(item)
        else:
            item.count -= count

    async def craft(self, telegram_id: int, craft_data: CraftItemSchema) -> list[ItemSchema]:
        player = await get_player_with_resources_for_craft(
            self.session,
            telegram_id,
            craft_data.map_id
        )
        item = await get_item_for_craft(self.session, craft_data.item_id)
        can_player_craft_item(player, item)
        player_id = player.id
        for recipe in item.recipe:
            PlayerService.update_resources(
                player.resources, recipe.resource_id, recipe.resource_quantity, "decrease"
            )

        await self._update_inventory_items_after_craft(player, item)

        await BaseService.commit_or_rollback(self.session)

        player_inventory = await get_player_inventory(self.session, player_id)
        return serialize_items(player_inventory)

    async def _update_inventory_items_after_craft(self, player: Player, item: Item) -> None:
        player.inventory.sort(key=lambda i: i.count)

        if not player.inventory or not any(inv.item == item for inv in player.inventory):
            await create_player_inventory(self.session, player.id, item.id)
        else:
            for items in player.inventory:
                if items.item_id == item.id and items.count < item.max_count:
                    items.count += 1
                    return
            await create_player_inventory(self.session, player.id, item.id)


class ItemTransferService(BaseTransferService):
    async def transfer(self, telegram_id: int, transfer_data: TransferItemSchema) -> PlayerItemsSchema:
        player = await get_player_with_items(self.session, telegram_id, transfer_data.map_id)
        validate_player(player)
        player_id = player.id
        can_player_transfer_items(player, transfer_data.direction.value)
        await self._update_items_after_transfer(player, transfer_data.item_id, transfer_data.direction.value,
                                                transfer_data.count)
        await BaseService.commit_or_rollback(self.session)
        player = await get_player_with_all_items(self.session, player_id)
        return serialize_player_items(player)

    async def _update_items_after_transfer(self, player: Player, item_id: int, direction: str, count: int) -> None:
        if direction == "to_storage":
            await self._move_item_to_storage(player, item_id, count)
        elif direction == "from_storage":
            await self._move_item_from_storage(player, item_id, count)

    async def _move_item(
            self,
            source_item: PlayerItemStorage | Inventory,
            count: int,
            target_container: ItemContainer
    ) -> None:
        max_count = source_item.item.max_count  # type: ignore[attr-defined]
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

    async def _move_item_to_storage(self, player: Player, item_id: int, count: int) -> None:
        item = await inventory_repository.get_by_id(self.session, item_id)
        validate_item_before_transfer(item, player.id, count)
        container = StorageContainer(player)
        await self._move_item(item, count, container)

    async def _move_item_from_storage(self, player: Player, item_id: int, count: int) -> None:
        item = await player_item_storage_repository.get_by_id(self.session, item_id)
        validate_item_before_transfer(item, player.id, count)
        container = InventoryContainer(player)
        await self._move_item(item, count, container)


class ItemEquipService(BaseService):

    async def equip(self, telegram_id: int, equip_data: EquipItemSchema) -> PlayerEquipItemResponseSchema:
        player = await get_player_with_stats(self.session, telegram_id=telegram_id, map_id=equip_data.map_id)
        validate_player(player)
        player_id = player.id
        player_inventory_item = await get_inventory_item_with_stats(self.session, player.id, equip_data.item_id)
        validate_inventory_item(player_inventory_item)
        player_equip_item = await get_equip_item_with_specific_type(
            self.session, player_id=player.id, item_type=player_inventory_item.item.type
        )
        await self.update_items(player, player_equip_item, player_inventory_item)
        await BaseService.commit_or_rollback(self.session)

        player_items = await get_player_with_all_items(self.session, player_id)
        return PlayerEquipItemResponseSchema(stats=player.stats, items=serialize_player_items(player_items))

    async def unequip(self, telegram_id: int, equip_data: EquipItemSchema) -> PlayerEquipItemResponseSchema:
        player = await get_player_with_inventory_items(self.session, telegram_id=telegram_id, map_id=equip_data.map_id)
        validate_player(player)
        player_id = player.id
        player_equip_item = await equip_item_repository.get(self.session, id=equip_data.item_id, player_id=player_id)
        validate_player_before_unequip_item(player_equip_item, player)
        self._update_stats(player_equip_item.item.stats, player, "unequip")
        create_inventory_item(
            self.session, player_equip_item.item_id, player.id, player_equip_item.tier
        )
        await self.session.delete(player_equip_item)
        await BaseService.commit_or_rollback(self.session)
        player_items = await get_player_with_all_items(self.session, player_id)
        return PlayerEquipItemResponseSchema(stats=player.stats, items=serialize_player_items(player_items))

    async def update_items(self, player: Player, player_equip_item: EquipItem,
                           player_inventory_item: Inventory) -> None:
        if player_equip_item:
            self._update_stats(player_equip_item.item.stats, player, "unequip")
            create_inventory_item(
                self.session, player_equip_item.item_id, player.id, player_equip_item.tier
            )
            await self.session.delete(player_equip_item)
        create_equip_item(
            self.session, player_id=player.id, item_id=player_inventory_item.item.id, tier=player_inventory_item.tier
        )
        self._update_stats(player_inventory_item.item.stats, player, "equip")
        await self.session.delete(player_inventory_item)

    def _update_stats(self, item_stats: ItemStat, player: Player, operation: str) -> None:
        for stat in item_stats.__annotations__:
            if stat != id:
                if hasattr(player.stats, stat):
                    item_value = getattr(item_stats, stat)
                    player_value = getattr(player.stats, stat)
                    setattr(player.stats, stat, player_value + item_value
                    if operation == "equip" else player_value - item_value)
