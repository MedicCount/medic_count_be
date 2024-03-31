from pydantic import BaseModel

class MedicineData(BaseModel):
    counts: int
    uid: str
    name: str
    image: str
    groupId: str
    lables: list

class MedicineGroupData(BaseModel):
    createdDate: float
    groupName: str
    uid: str