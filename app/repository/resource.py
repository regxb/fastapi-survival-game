from app.models import Resource
from app.repository import BaseRepository

RepositoryResource = BaseRepository[Resource]
repository_resource = RepositoryResource(Resource)
