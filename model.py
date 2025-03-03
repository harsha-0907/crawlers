# This is a place for all the models that will be used in the project

from pydantic import BaseModel
from typing import List

class Url(BaseModel):
    url: str = None
    index: int = None
    egress: List[int] = None
    