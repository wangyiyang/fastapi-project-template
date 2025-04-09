from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field as SQLModelField
from sqlmodel import Relationship, SQLModel

if TYPE_CHECKING:
    from project_name.security import User


class Content(SQLModel, table=True):
    """This is an example model for your application.

    Replace with the *things* you do in your application.
    """

    id: Optional[int] = SQLModelField(default=None, primary_key=True)
    title: str
    slug: str = SQLModelField(default=None)
    text: str
    published: bool = False
    created_time: str = SQLModelField(
        default_factory=lambda: datetime.now().isoformat()
    )
    tags: str = SQLModelField(default="")
    user_id: Optional[int] = SQLModelField(foreign_key="user.id")

    # It populates a `.contents` attribute to the `User` model.
    user: Optional["User"] = Relationship(back_populates="contents")
