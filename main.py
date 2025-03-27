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
        result = await db.Sprites.insert_one(sprite_doc)
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
        result = await db.Audio.insert_one(audio_doc)
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
        result = await db.Scores.insert_one(score_doc)
        return {"message": "Score recorded", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        # Explicitly close connection (critical for Vercel)
        await shutdown_db()

# Retrieve sprites
@app.get("/get_sprites/", summary="Retrieve all uploaded sprites", response_description="List of sprite files")
async def get_sprites():
    try:
        db = get_db()
        sprite_cursor = db.Sprites.find()
        sprites = []
        async for sprite in sprite_cursor:
            sprites.append({
                "filename": sprite.get("filename"),
                "description": sprite.get("description")
            })
        return {"sprites": sprites}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        await shutdown_db()

# Retrieve audio files
@app.get("/get_audio/", summary="Retrieve all uploaded audio files", response_description="List of audio files")
async def get_audio():
    try:
        db = get_db()
        audio_cursor = db.Audio.find()
        audio_files = []
        async for audio in audio_cursor:
            audio_files.append({
                "filename": audio.get("filename"),
                "description": audio.get("description")
            })
        return {"audio": audio_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        await shutdown_db()

# Retrieve player score
@app.get("/get_scores/", summary="Retrieve all player scores", response_description="List of player scores")
async def get_scores():
    try:
        db = get_db()
        scores_cursor = db.Scores.find()
        scores = []
        async for score in scores_cursor:
            scores.append({
                "player_name": score.get("player_name"),
                "score": score.get("score")
            })
        return {"scores": scores}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        await shutdown_db()