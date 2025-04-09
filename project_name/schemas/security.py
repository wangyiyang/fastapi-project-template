from typing import List, Optional
from pydantic import BaseModel, Field

from ..schemas.base import RequestModel, ResponseModel


class Token(ResponseModel):
    """令牌响应模型"""
    class TokenData(BaseModel):
        access_token: str
        refresh_token: str
        token_type: str

    data: Optional[TokenData] = None


class RefreshToken(RequestModel):
    """刷新令牌请求模型"""
    refresh_token: str


class TokenData(BaseModel):
    """令牌数据模型"""
    username: Optional[str] = None


class UserResponse(ResponseModel):
    """用户响应模型"""
    class UserData(BaseModel):
        """用户数据模型"""
        id: int
        username: str
        disabled: bool
        superuser: bool
        contents: Optional[List] = Field(default_factory=lambda: [])

    data: Optional[UserData] = None

    def __init__(self, **kwargs):
        if "data" not in kwargs:
            data = self.UserData(**kwargs)
            kwargs = {"data": data, "code": 200, "message": "成功获取用户信息"}
        super().__init__(**kwargs)


class UserCreate(RequestModel):
    """用户创建请求模型"""
    username: str
    password: str
    superuser: bool = False
    disabled: bool = False


class UserPasswordPatch(RequestModel):
    """用户密码更新请求模型"""
    password: str
    password_confirm: str
