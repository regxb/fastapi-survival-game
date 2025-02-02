from app.models import Item
from app.repository import BaseRepository

ItemRepository = BaseRepository[Item]
item_repository = ItemRepository(Item)
