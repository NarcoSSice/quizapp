import os
import uuid
from fastapi import UploadFile, Request
from typing import Literal

from core.exceptions.media import NotSupportedExtensionsException


class MediaManager:
    SUPPORTED_EXTENSIONS: set[str] = {"jpg", "jpeg", "png", "webp", "svg"}
    MEDIA_SUBDIR: Literal["users"] = "users"

    def __init__(self):
        self.target_dir = os.path.join("app/media", self.MEDIA_SUBDIR)
        os.makedirs(self.target_dir, exist_ok=True)

    async def save(self, image: UploadFile, request: Request) -> str:
        ext = image.filename.split(".")[-1].lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise NotSupportedExtensionsException

        filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(self.target_dir, filename)

        with open(file_path, "wb") as buffer:
            buffer.write(await image.read())

        image_url = str(
            request.url_for("media", path=f"{self.MEDIA_SUBDIR}/{filename}")
        )
        return image_url


media_utils = MediaManager()
