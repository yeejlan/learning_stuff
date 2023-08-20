
from exception import UserException
from models import user_model

async def getAuthorizedUser() -> user_model.UserModel:
    user_id = 9 # get user_id from auth
    if user_id < 1:
        raise UserException("bad user id", 401)

    user = await user_model.getUserById(user_id)
    if user is None:
        raise UserException("not authorized user", 401)

    return user