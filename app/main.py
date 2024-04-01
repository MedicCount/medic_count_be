from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse
from PIL import Image
import io
import os
from yolov5.detect import run
from services.firebase import authen, f_store, storage, timestamp
from typing import Optional
from model.medicine import MedicineData, MedicineGroupData

app = FastAPI()

ai_path = 'app/ai/win_best.pt'
project_path = 'app/ai/result'
image_path = 'app/ai/image/tmp.jpg'

bucket = storage.bucket()

def verify_user(uid):
    try:
        user = authen.get_user(uid)
        if user is None:
            raise HTTPException(status_code=404, detail='User not found')
        return user
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def verify_permission(uid, provideId, idType):
    try:
        user = verify_user(uid)
        tmp = f_store.collection(idType).document(provideId)
        if user.uid != tmp.get().to_dict()['_uid']:
            raise HTTPException(status_code=403, detail='Permission denied')
        return tmp
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def perform_detection(image, uid):
    try:
        pil_image = Image.open(io.BytesIO(image))
        pil_image.save(image_path)

        run(
            weights=ai_path,
            source=image_path,
            project=project_path,
            name=f"{uid}",
            save_txt=True,
            exist_ok=True
        )

        with open(f'{project_path}/{uid}/labels/tmp.txt', 'r') as f:
            res_labels = f.readlines()

        res_labels = [i.replace("\n", "").split(" ") for i in res_labels]

        detected_image = Image.open(f'{project_path}/{uid}/tmp.jpg')
        res_img_bin = io.BytesIO()
        detected_image.save(res_img_bin, format=detected_image.format)
        res_img_bin = res_img_bin.getvalue()

        return res_labels, res_img_bin
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return {"message": "Hello MediCount!"}

@app.post("/detect/")
async def detect(
    mgid: Optional[str] = Form(None), 
    uid: str = Form(...), 
    file: UploadFile = File(...)
):
    verify_user(uid)

    directory = os.path.join(project_path, uid, 'labels')
    os.makedirs(directory, exist_ok=True)

    local_image_path = f"{project_path}/{uid}/tmp.jpg"
    local_label_path = f"{project_path}/{uid}/labels/tmp.txt"

    # Clean up tmp.txt
    with open(local_label_path, 'w') as f:
        f.write('')

    image = await file.read()
    res_labels, res_img_bin = await perform_detection(image, uid)

    if mgid is None:

        mg_data: MedicineGroupData = {
            'createdDate': timestamp,
            'groupName': 'unknown',
            '_uid': uid,
        }

        medicineGroup = f_store.collection('medicineGroup').document()
        medicineGroup.set(mg_data)
        mgid = medicineGroup.id

    elif f_store.collection('medicineGroup').document(mgid).get().exists is False:
        return HTTPException(status_code=404, detail='Medicine Group not found')

    m_data: MedicineData = {
        'counts': len(res_labels),
        '_uid': uid,
        'name': 'unknown',
        '_image': 'unknown',
        'groupId': mgid,
        'lables': [{'row': i, 'data': row} for i, row in enumerate(res_labels)]
    }

    medicine = f_store.collection('medicine').document()
    medicine.set(m_data)

    destination = f"{uid}/{medicine.id}/tmp.jpg"
    blob = bucket.blob(destination)
    blob.upload_from_filename(local_image_path)

    medicine.update({
        '_image': destination
    })

    return {
        'status': 'success',
        'firestore': {
            'medicine': medicine.id,
            'medicineGroup': mgid,
        },
        'storage': destination,
    }

@app.get("/get_image/")
async def get_image(
    uid: str = Form(...), 
    mid: str = Form(...)
):
    medicine = verify_permission(uid, mid, idType='medicine')
    local_image_path = f"{project_path}/{uid}/tmp.jpg"

    medicine_image = medicine.get().to_dict()['image']
    blob = bucket.blob(medicine_image)
    blob.download_to_filename(local_image_path)
    
    return FileResponse(local_image_path, media_type='image/jpeg')

@app.get("/get_counts/")
async def get_counts(
    uid: str = Form(...), 
    mid: str = Form(...)
):
    medicine = verify_permission(uid, mid, idType='medicine')
    medicine_counts = medicine.get().to_dict()['counts']

    return {
        'status': 'success',
        'counts': medicine_counts,
    }

# TODO: Update

@app.put("/update_medicine/")
async def update_medicine(
    data: MedicineData,
    uid: str,
    mid: str
):
    medicine = verify_permission(uid, mid, idType='medicine')
    data = data.dict(exclude_unset=True)
    medicine.update(data)

    return {
        'status': 'success',
        'data': data,
    }

@app.put("/update_medicine_group/")
async def update_medicine_group(
    data: MedicineGroupData,
    uid: str,
    mgid: str,
):
    medicineGroup = verify_permission(uid, mgid, idType='medicineGroup')
    data = data.dict(exclude_unset=True)
    medicineGroup.update(data)

    return {
        'status': 'success',
        'data': data,
    }

# TODO: Delete

@app.delete("/delete_medicine/")
async def delete_medicine(
    uid: str = Form(...),
    mid: str = Form(...),
):
    medicine = verify_permission(uid, mid, idType='medicine')
    medicine.delete()

    destination = f"{uid}/{medicine.id}/tmp.jpg"
    blob = bucket.blob(destination)
    blob.delete()

    return {
        'status': 'success',
    }

@app.delete("/delete_medicine_group/")
async def delete_medicine_group(
    uid: str = Form(...),
    mgid: str = Form(...),
):
    medicineGroup = verify_permission(uid, mgid, idType='medicineGroup')
    medicineGroup.delete()

    return {
        'status': 'success',
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
