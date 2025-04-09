from typing import List, Optional, Union

from ..schemas.base import RequestModel, ResponseModel


class ContentResponse(ResponseModel):
    """内容响应模型"""

    class ContentData:
        """内容数据模型"""

        id: int
        title: str
        slug: str
        text: str
        published: bool
        created_time: str
        tags: List[str]
        user_id: int

    data: Optional[ContentData] = None

    def __init__(self, **kwargs):
        # 处理标签字符串到列表的转换
        tags = kwargs.pop("tags", None)
        if "data" not in kwargs:
            if tags and isinstance(tags, str):
                kwargs["tags"] = tags.split(",")
            data = self.ContentData(**kwargs)
            kwargs = {"data": data, "code": 200, "message": "成功获取内容"}
        super().__init__(**kwargs)


class ContentIncoming(RequestModel):
    """内容创建/更新请求模型"""

    title: Optional[str] = None
    text: Optional[str] = None
    published: Optional[bool] = False
    tags: Optional[Union[List[str], str]] = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        # 标签列表转换为字符串（用于存储）
        tags = kwargs.pop("tags", None)
        if tags and isinstance(tags, list):
            kwargs["tags"] = ",".join(tags)
        super().__init__(**kwargs)
        self.generate_slug()

    def generate_slug(self):
        """从标题生成 slug"""
        if hasattr(self, "title") and self.title:
            self.slug = self.title.lower().replace(" ", "-")
