from pydantic import BaseModel
from datetime import datetime

class MedicineData(BaseModel):
    counts: int
    _uid: str
    name: str
    _image: str
    groupId: str
    lables: list

class MedicineGroupData(BaseModel):
    createdDate: datetime = datetime.now()
    groupName: str
    _uid: str