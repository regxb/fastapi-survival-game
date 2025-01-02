from fastapi import HTTPException
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.crud.base import CRUDBase
from app.models.maps import MapObject, PlayerBase
from app.models.players import Player
from app.schemas.players import PlayerCreateSchema

CRUDPlayers = CRUDBase[Player, PlayerCreateSchema]
base_crud_player = CRUDPlayers(Player)


async def create_player(session: AsyncSession, map_id: int, telegram_id: int):
    player = Player(map_id=map_id, user_id=telegram_id)
    session.add(player)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=404, detail="Map not found")
    return player


async def get_player_with_map_object(session: AsyncSession, map_id: int, telegram_id: int):
    stmt = (select(Player).
            options(joinedload(Player.map_object)).
            where(and_(Player.map_id == map_id, Player.user_id == telegram_id))
            )
    result = await session.scalar(stmt)
    if not result:
        raise HTTPException(status_code=404, detail="Player not found")
    return result


async def get_player_with_position(session: AsyncSession, player_id: int):
    stmt = (
        select(Player)
        .options(
            joinedload(Player.map_object).joinedload(MapObject.position)
        )
        .where(Player.id == player_id)
    )

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_player_base(session: AsyncSession, map_object_id: int, map_id: int, telegram_id: int):
    player_base = PlayerBase(
        map_object_id=map_object_id,
        map_id=map_id,
        owner_id=telegram_id
    )
    session.add(player_base)
    try:
        await session.flush()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400)
    return player_base
