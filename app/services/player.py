from aiogram.utils.web_app import WebAppUser
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Player, PlayerResources
from app.repository import (create_new_player, farm_session_repository,
                            get_all_players, get_player_with_base,
                            get_player_with_resources_and_items,
                            map_object_repository, map_repository,
                            player_repository, create_player_stats, get_player_with_stats)
from app.schemas import (BasePlayerSchema, PlayerCreateSchema,
                         PlayerMoveResponseSchema, PlayerMoveSchema,
                         PlayerSchema)
from app.serialization.player import player_serialize
from app.services.base import BaseService
from app.validation.map import validate_map, validate_map_object
from app.validation.player import (can_player_do_something,
                                   can_player_move_to_new_map_object,
                                   validate_player)


class PlayerService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_player(self, user: WebAppUser, player_data: PlayerCreateSchema) -> PlayerSchema:
        map_ = await map_repository.get_by_id(self.session, player_data.map_id)
        validate_map(map_)
        new_player = create_new_player(self.session, user.id, user.username, player_data.map_id)  # type: ignore
        await self.session.flush()
        create_player_stats(self.session, new_player.id)
        await BaseService.commit_or_rollback(self.session)
        player = await get_player_with_stats(self.session, telegram_id=user.id, map_id=player_data.map_id)
        return PlayerSchema(in_base=False, **player.__dict__)

    async def get_players(self, telegram_id: int) -> list[BasePlayerSchema]:
        players = await get_all_players(self.session, telegram_id)
        return [BasePlayerSchema.model_validate(player) for player in players]

    async def get(self, map_id: int, telegram_id: int) -> PlayerSchema:
        player = await get_player_with_resources_and_items(self.session, telegram_id, map_id)
        validate_player(player)

        farm_session = await farm_session_repository.get(
            self.session,
            player_id=player.id,
            map_id=map_id,
            status="in_progress"
        )
        return player_serialize(player, farm_session)

    async def move(self, telegram_id: int, player_data: PlayerMoveSchema) -> PlayerMoveResponseSchema:
        player = await get_player_with_base(self.session, telegram_id, player_data.map_id)
        validate_player(player)
        map_object = await map_object_repository.get_by_id(self.session, id=player_data.map_object_id)
        validate_map_object(map_object)
        can_player_do_something(player)
        can_player_move_to_new_map_object(player.map_object_id, player_data.map_object_id)
        self._change_player_status(player, map_object.id)
        player.map_object_id = player_data.map_object_id
        player_id = player.id
        await BaseService.commit_or_rollback(self.session)
        return PlayerMoveResponseSchema(new_map_object_id=player_data.map_object_id, player_id=player_id)

    @staticmethod
    def _change_player_status(player: Player, map_object_id: int) -> None:
        if player.base and map_object_id == player.base.map_object_id:
            player.status = "recovery"
        else:
            player.status = "waiting"

    async def update_energy(self) -> None:
        where_clause = {"energy": ("<", 100), "status": "recovery"}

        update_data = {"energy": Player.energy + 1}

        updated_count = await player_repository.update_multiple(
            session=self.session,
            model=Player,
            obj_in=update_data,
            where_clause=where_clause,
        )
        print(f"Updated {updated_count} rows")

    async def update_health(self) -> None:
        where_clause = {"health": ("<", 100), "status": "recovery"}

        update_data = {"health": Player.health + 1}

        updated_count = await player_repository.update_multiple(
            session=self.session,
            model=Player,
            obj_in=update_data,
            where_clause=where_clause,
        )
        print(f"Updated {updated_count} rows")

    @staticmethod
    def update_resources(
            player_resources: list[PlayerResources],
            resource_id: int,
            quantity: int,
            action: str
    ) -> None:
        for resource in player_resources:
            if resource.resource_id == resource_id:
                if action == "decrease":
                    resource.resource_quantity -= quantity
                if action == "increase":
                    resource.resource_quantity += quantity
