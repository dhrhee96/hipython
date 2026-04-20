from fastapi import FastAPI, UploadFile, File, HTTPException
from s3_client import s3, BUCKET_NAME
import uuid

app = FastAPI()


# 이미지 업로드
@app.post("/images")
async def upload_image(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1]
    key = f"{uuid.uuid4()}.{ext}"

    try:
        s3.upload_fileobj(
            file.file,
            BUCKET_NAME,
            key,
            ExtraArgs={"ContentType": file.content_type},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    url = f"https://{BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/{key}"
    return {"filename": key, "url": url}


# 이미지 목록 조회
@app.get("/images")
def list_images():
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    objects = response.get("Contents", [])

    images = [
        {
            "filename": obj["Key"],
            "url": f"https://{BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/{obj['Key']}",
            "size": obj["Size"],
            "last_modified": str(obj["LastModified"]),
        }
        for obj in objects
    ]
    return {"count": len(images), "images": images}


# 이미지 삭제
@app.delete("/images/{filename}")
def delete_image(filename: str):
    try:
        s3.delete_object(Bucket=BUCKET_NAME, Key=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": f"{filename} 삭제 완료"}