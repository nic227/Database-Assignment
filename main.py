from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import base64
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = FastAPI()


# Initialize MongoDB connection (only when needed)
def get_db():
    client = AsyncIOMotorClient(os.getenv("MONGODB_CONNECTION_STRING"))
    return client.get_database()

# Close connection during app shutdown
@app.on_event("shutdown")
async def shutdown_db():
    client = AsyncIOMotorClient(os.getenv("MONGODB_CONNECTION_STRING"))
    client.close()
    

# Model for player scores
class PlayerScore(BaseModel):
    player_name: str
    score: int

# Upload sprite (Base64)
@app.post("/upload_sprite/", summary="Upload a sprite image", response_description="ID of the uploaded sprite")
async def upload_sprite(file: UploadFile = File(...)):
    try:
        db = get_db()  # Get fresh database instance
        content = await file.read()
        encoded = base64.b64encode(content).decode("utf-8")
        sprite_doc = {
            "filename": file.filename,
            "content": encoded,
            "description": "Sprite uploaded via Base64"
        }
        result = await db.sprites.insert_one(sprite_doc)
        return {"message": "Sprite uploaded", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        # Explicitly close connection (critical for Vercel)
        await shutdown_db()

# Upload audio (Base64)
@app.post("/upload_audio/", summary="Upload an audio file", response_description="ID of the uploaded audio")
async def upload_audio(file: UploadFile = File(...)):
    try:
        db = get_db()  # Get fresh database instance
        content = await file.read()
        encoded = base64.b64encode(content).decode("utf-8")
        audio_doc = {
            "filename": file.filename,
            "content": encoded,
            "description": "Audio uploaded via Base64"
        }
        result = await db.audio.insert_one(audio_doc)
        return {"message": "Audio uploaded", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        # Explicitly close connection (critical for Vercel)
        await shutdown_db()

# Upload player score
@app.post("/upload_score/", summary="Submit a player score", response_description="ID of the recorded score")
async def upload_score(score: PlayerScore):
    try:
        db = get_db()  # Get fresh database instance
        score_doc = score.dict()
        result = await db.scores.insert_one(score_doc)
        return {"message": "Score recorded", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        # Explicitly close connection (critical for Vercel)
        await shutdown_db()