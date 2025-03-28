from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated
from motor.motor_asyncio import AsyncIOMotorClient
import base64
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Initialise MongoDB connection only when needed
def get_db():
    client = AsyncIOMotorClient(os.getenv("MONGODB_CONNECTION_STRING"))
    return client.get_database()

# Close MongoDB connection
async def shutdown_db():
    client = AsyncIOMotorClient(os.getenv("MONGODB_CONNECTION_STRING"))
    client.close()

class PlayerScore(BaseModel):
    player_name: Annotated[
        str, 
        StringConstraints(
            pattern=r"^[a-zA-Z0-9_ ]+$", 
            min_length=1, 
            max_length=50
        )
    ] = Field(strict=True)
    score: int

def sanitize_input(input_str: str) -> str:
    # Remove special characters that could enable NoSQL injection
    return re.sub(r"[^\w\s]", "", input_str).strip()

# ==== File Upload Security ==== #
ALLOWED_SPRITE_TYPES = ["image/png", "image/jpeg"]
ALLOWED_AUDIO_TYPES = ["audio/mpeg", "audio/wav"]
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# ==== Upload Endpoints ==== #
@app.post("/upload_sprite/", summary="Upload a sprite image", response_description="ID of the uploaded sprite")
async def upload_sprite(file: UploadFile = File(...)):
    try:
        db = get_db()
        # Task 4c: File validation
        if file.content_type not in ALLOWED_SPRITE_TYPES:
            raise HTTPException(400, "Only PNG/JPEG images allowed")

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(400, "File exceeds 5MB limit")

        # Sanitize filename
        clean_filename = sanitize_input(file.filename)
        
        encoded = base64.b64encode(content).decode("utf-8")
        sprite_doc = {
            "filename": clean_filename,
            "content": encoded,
            "description": "Sprite uploaded via Base64"
        }
        result = await db.Sprites.insert_one(sprite_doc)
        return {"message": "Sprite uploaded", "id": str(result.inserted_id)}
    
    except Exception as e:
        raise HTTPException(500, f"Server error: {str(e)}")
    finally:
        await shutdown_db()

@app.post("/upload_audio/", summary="Upload an audio file", response_description="ID of the uploaded audio")
async def upload_audio(file: UploadFile = File(...)):
    try:
        db = get_db()
        if file.content_type not in ALLOWED_AUDIO_TYPES:
            raise HTTPException(400, "Only MP3/WAV audio allowed")

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(400, "File exceeds 5MB limit")

        clean_filename = sanitize_input(file.filename)
        
        encoded = base64.b64encode(content).decode("utf-8")
        audio_doc = {
            "filename": clean_filename,
            "content": encoded,
            "description": "Audio uploaded via Base64"
        }
        result = await db.Audio.insert_one(audio_doc)
        return {"message": "Audio uploaded", "id": str(result.inserted_id)}
    
    except Exception as e:
        raise HTTPException(500, f"Server error: {str(e)}")
    finally:
        await shutdown_db()

@app.post("/upload_score/", summary="Submit a player score", response_description="ID of the recorded score")
async def upload_score(score: PlayerScore):
    try:
        db = get_db()
        sanitized_name = sanitize_input(score.player_name)
        
        score_doc = {
            "player_name": sanitized_name,
            "score": score.score
        }
        result = await db.Scores.insert_one(score_doc)
        return {"message": "Score recorded", "id": str(result.inserted_id)}
    
    except Exception as e:
        raise HTTPException(500, f"Server error: {str(e)}")
    finally:
        await shutdown_db()


# ==== Retrieval Endpoints ==== #

@app.get("/get_sprites/")
async def get_sprites():
    try:
        db = get_db()
        cursor = db.Sprites.find()
        data = []
        async for doc in cursor:
            data.append({
                "filename": doc.get("filename"),
                "description": doc.get("description")
            })
        return {"sprites": data}
    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")
    finally:
        await shutdown_db()

@app.get("/get_audio/")
async def get_audio():
    try:
        db = get_db()
        cursor = db.Audio.find()
        data = []
        async for doc in cursor:
            data.append({
                "filename": doc.get("filename"),
                "description": doc.get("description")
            })
        return {"audio": data}
    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")
    finally:
        await shutdown_db()

@app.get("/get_scores/")
async def get_scores():
    try:
        db = get_db()
        cursor = db.Scores.find()
        data = []
        async for doc in cursor:
            data.append({
                "player_name": doc.get("player_name"),
                "score": doc.get("score")
            })
        return {"scores": data}
    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")
    finally:
        await shutdown_db()
