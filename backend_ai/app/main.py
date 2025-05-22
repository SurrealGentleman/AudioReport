from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Header
from starlette.status import HTTP_401_UNAUTHORIZED
import shutil
import uuid
import os
from prompts import report_prompt
from whisper_module import Whisper
from llama_module import Llama
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


# Загрузка .env файла
load_dotenv('.env')

# Инициализация
app = FastAPI()
whisper = Whisper(model_name=os.environ.get("WHISPER_MODEL"),
                  device=os.environ.get("DEVICE_FOR_AI"))
llama = Llama()


# Авторизация по API-ключу
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != os.environ.get("API_KEY"):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid API Key")



@app.get('/')
def root():
    return {"msg": "Hello"}


@app.post("/generate-report/")
async def generate_report(
        audio: UploadFile = File(...),
        meeting_date: str = Form(...),
        participants: str = Form(...),
        x_api_key: str = Depends(verify_api_key),
):

    # Сохраняем аудиофайл
    filename, ext = os.path.splitext(audio.filename)
    temp_filename = f"temp/temp_{uuid.uuid4()}{ext}"
    print(temp_filename)
    with open(temp_filename, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    try:
        transcript = whisper.transcribe(temp_filename)
        os.remove(temp_filename)
        prompt = report_prompt(transcript, participants, meeting_date)
        report = llama.generate(prompt)
        print(report)
        return {
            'report_text': report
        }
    except Exception as e:
        print(e)
