from pydantic import BaseModel
from datetime import datetime

class MedicineData(BaseModel):
    _mid: str
    counts: int
    _uid: str
    name: str
    _image: str
    groupId: str
    lables: list

class MedicineGroupData(BaseModel):
    _mgid: str
    _createdDate: datetime = datetime.now()
    groupName: str
    _uid: str