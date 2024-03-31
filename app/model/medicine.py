from pydantic import BaseModel

class MedicineData(BaseModel):
    counts: int
    uid: str
    name: str = 'unknown'
    image: str = 'unknown'
    groupId: str

class MedicineGroupData(BaseModel):
    createdDate: float
    groupName: str = 'unknown'