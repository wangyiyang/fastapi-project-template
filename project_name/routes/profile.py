from fastapi import APIRouter

from ..schemas.security import UserResponse
from ..security import AuthenticatedUser, User

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
async def my_profile(current_user: User = AuthenticatedUser):
    return UserResponse(data=current_user)
