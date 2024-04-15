from typing import Optional

from pydantic import BaseModel


class TaskOut(BaseModel):
    id: int
    status: str
    result: Optional[str] = None
