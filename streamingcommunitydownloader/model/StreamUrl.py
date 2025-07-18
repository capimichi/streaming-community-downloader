from typing import Optional
from pydantic import BaseModel

class StreamUrl(BaseModel):
    url: str
    title: Optional[str] = None
    season_number: Optional[int] = None
    episode_number: Optional[int] = None

