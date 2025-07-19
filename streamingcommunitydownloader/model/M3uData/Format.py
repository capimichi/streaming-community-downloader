from typing import Optional, Dict
from pydantic import BaseModel

class Format(BaseModel):
    format_id: Optional[str] = None
    format_note: Optional[str] = None
    format_index: Optional[int] = None
    url: Optional[str] = None
    manifest_url: Optional[str] = None
    language: Optional[str] = None
    ext: Optional[str] = None
    protocol: Optional[str] = None
    preference: Optional[int] = None
    quality: Optional[int] = None
    has_drm: Optional[bool] = None
    vcodec: Optional[str] = None
    acodec: Optional[str] = None
    dynamic_range: Optional[str] = None
    video_ext: Optional[str] = None
    audio_ext: Optional[str] = None
    vbr: Optional[float] = None
    abr: Optional[float] = None
    tbr: Optional[float] = None
    resolution: Optional[str] = None
    aspect_ratio: Optional[float] = None
    fps: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    http_headers: Optional[Dict[str, str]] = None
    format: Optional[str] = None