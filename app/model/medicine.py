from pydantic import BaseModel
from datetime import datetime
from ..services.firebase import timestamp

class MedicineData(BaseModel):
    counts: int
    _uid: str
    name: str
    _image: str
    groupId: str
    lables: list

class MedicineGroupData(BaseModel):
    createdDate: datetime = timestamp
    groupName: str
    _uid: str