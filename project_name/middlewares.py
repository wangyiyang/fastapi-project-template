from typing import Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from .schemas import ResponseCode, ResponseModel


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器"""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        """处理HTTP异常"""
        return JSONResponse(
            status_code=200,  # 始终返回200，状态在响应体中表示
            content=ResponseModel.from_exception(
                exc.status_code, exc.detail
            ).dict(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """处理请求验证异常"""
        error_messages = []
        for error in exc.errors():
            loc = " -> ".join([str(l) for l in error["loc"]])
            msg = f"{loc}: {error['msg']}"
            error_messages.append(msg)

        detail = "请求参数验证失败: " + "; ".join(error_messages)
        return JSONResponse(
            status_code=200,  # 始终返回200，状态在响应体中表示
            content=ResponseModel.from_exception(
                ResponseCode.BAD_REQUEST, detail
            ).dict(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """处理通用异常"""
        return JSONResponse(
            status_code=200,  # 始终返回200，状态在响应体中表示
            content=ResponseModel.error(
                code=ResponseCode.INTERNAL_ERROR,
                message=f"服务器内部错误: {str(exc)}",
            ).dict(),
        )


class ResponseMiddleware:
    """响应中间件，将所有响应格式标准化"""

    def __init__(self, app: FastAPI, exclude_paths: Optional[list] = None):
        self.app = app
        self.exclude_paths = exclude_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if any(path.startswith(exclude) for exclude in self.exclude_paths):
            await self.app(scope, receive, send)
            return

        # 自定义发送响应的函数
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # 保存原始状态码
                message["status"]
                message["status"] = 200  # 始终返回200
                await send(message)
            elif message["type"] == "http.response.body":
                # 如果是JSON响应，转换为标准格式
                body = message.get("body", b"")
                if not body:
                    await send(message)
                    return

                import json

                try:
                    # 尝试解析JSON
                    data = json.loads(body.decode())
                    # 检查是否已经是标准格式
                    if not (
                        isinstance(data, dict)
                        and "code" in data
                        and "message" in data
                    ):
                        # 转换为标准格式
                        standardized = ResponseModel.success(data=data).dict()
                        body = json.dumps(standardized).encode()
                        message["body"] = body
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # 不是JSON或无法解码，保持原样
                    pass
                await send(message)
            else:
                await send(message)

        await self.app(scope, receive, send_wrapper)


def setup_middlewares(app: FastAPI) -> None:
    """设置所有中间件"""
    # 添加响应中间件
    app.add_middleware(ResponseMiddleware)
    # 注册异常处理器
    register_exception_handlers(app)
