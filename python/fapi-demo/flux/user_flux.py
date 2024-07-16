
from core.exception import UserException
from core.reply import Reply
from models import user_model


async def getAuthorizedUser(user_id: int) -> user_model.UserModel:
    user = await user_model.getUserById(user_id)
    if not user:
        raise UserException('User not found', Reply.RESOURCE_NOT_FOUND)
    return user