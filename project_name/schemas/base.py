from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field
from enum import Enum
from http import HTTPStatus


class ResponseCode(int, Enum):
    """响应状态码枚举"""
    SUCCESS = 200  # 成功
    CREATED = 201  # 创建成功
    ACCEPTED = 202  # 请求已接受
    BAD_REQUEST = 400  # 请求错误
    UNAUTHORIZED = 401  # 未授权
    FORBIDDEN = 403  # 禁止访问
    NOT_FOUND = 404  # 资源不存在
    METHOD_NOT_ALLOWED = 405  # 方法不允许
    CONFLICT = 409  # 资源冲突
    TOO_MANY_REQUESTS = 429  # 请求过多
    INTERNAL_ERROR = 500  # 服务器错误
    NOT_IMPLEMENTED = 501  # 未实现
    BAD_GATEWAY = 502  # 网关错误
    SERVICE_UNAVAILABLE = 503  # 服务不可用


T = TypeVar('T')


class ResponseModel(Generic[T], BaseModel):
    """标准API响应模型"""
    code: int = Field(ResponseCode.SUCCESS, description="响应状态码")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")

    @classmethod
    def success(cls, data: Optional[T] = None, message: str = "操作成功") -> "ResponseModel[T]":
        """成功响应"""
        return cls(code=ResponseCode.SUCCESS, message=message, data=data)

    @classmethod
    def error(cls, code: int = ResponseCode.BAD_REQUEST, message: str = "操作失败", data: Optional[T] = None) -> "ResponseModel[T]":
        """错误响应"""
        return cls(code=code, message=message, data=data)

    @classmethod
    def from_exception(cls, status_code: int, detail: str, data: Optional[T] = None) -> "ResponseModel[T]":
        """从异常创建响应"""
        return cls(code=status_code, message=detail, data=data)


class PaginationParams(BaseModel):
    """分页查询参数"""
    page: int = Field(1, gt=0, description="页码")
    size: int = Field(10, gt=0, le=100, description="每页条数")


class PaginatedResponseModel(ResponseModel[T], Generic[T]):
    """分页响应模型"""
    class PaginationData(BaseModel, Generic[T]):
        items: List[T] = Field([], description="数据列表")
        total: int = Field(0, description="总条数")
        page: int = Field(1, description="当前页码")
        size: int = Field(10, description="每页条数")
        pages: int = Field(0, description="总页数")
        has_next: bool = Field(False, description="是否有下一页")
        has_prev: bool = Field(False, description="是否有上一页")

    data: Optional[PaginationData[T]] = None

    @classmethod
    def create(cls, items: List[T], total: int, page: int, size: int) -> "PaginatedResponseModel[T]":
        """创建分页响应"""
        pages = (total + size - 1) // size if size > 0 else 0
        pagination_data = cls.PaginationData[T](
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1
        )
        return cls(
            code=ResponseCode.SUCCESS,
            message="操作成功",
            data=pagination_data
        )


class RequestModel(BaseModel):
    """请求模型基类"""
    class Config:
        extra = "forbid"  # 禁止额外字段
        anystr_strip_whitespace = True  # 去除字符串前后空白


# 用于创建标准响应的快捷函数
def success_response(data: Any = None, message: str = "操作成功") -> Dict[str, Any]:
    """创建成功响应"""
    return ResponseModel.success(data, message).dict()


def error_response(code: int = ResponseCode.BAD_REQUEST, message: str = "操作失败") -> Dict[str, Any]:
    """创建错误响应"""
    return ResponseModel.error(code, message).dict()


def paginated_response(items: List, total: int, page: int, size: int) -> Dict[str, Any]:
    """创建分页响应"""
    return PaginatedResponseModel.create(items, total, page, size).dict()
