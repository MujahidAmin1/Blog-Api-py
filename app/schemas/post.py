from pydantic import BaseModel
from datetime import datetime

# what the client sends to CREATE a post
class PostCreate(BaseModel):
    title: str
    content: str
    img_url: str
    published: bool = False

# what the client sends to UPDATE a post
class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    img_url: str | None = None
    published: bool | None = None

# what the client sends to PATCH published status
class PostPatchPublished(BaseModel):
    published: bool

# what the API sends BACK (includes DB fields)
class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    user_id: int
    img_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}