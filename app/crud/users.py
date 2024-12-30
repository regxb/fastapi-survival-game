from app.crud.base import CRUDBase
from app.models.users import User
from app.schemas.users import UserCreateSchema

CRUDUsers = CRUDBase[User, UserCreateSchema]
base_crud_user = CRUDUsers(User)
