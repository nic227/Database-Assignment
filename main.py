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

# Create FastAPI instance
app = FastAPI()

# ========== Database Setup ========== #

# Initialise MongoDB connection only when needed
def get_db():
    client = AsyncIOMotorClient(os.getenv("MONGODB_CONNECTION_STRING"))
    return client.get_database()

# Close MongoDB connection
async def shutdown_db():
    client = AsyncIOMotorClient(os.getenv("MONGODB_CONNECTION_STRING"))
    client.close()

# ========== Input Model and Validation ========== #

#Pydantic model for player score with validation
 # Player name: must be 1-50 characters long, allow only alphanumeric characters, spaces and understores
class PlayerScore(BaseModel):
    player_name: Annotated[
        str, 
        StringConstraints(
            pattern=r"^[a-zA-Z0-9_ ]+$", 
            min_length=1, 
            max_length=50
        )
    ] = Field(strict=True)
    score: int  # Score must be an integer

def sanitize_input(input_str: str) -> str:
    # Remove special characters that could enable NoSQL injection
    return re.sub(r"[^\w\s]", "", input_str).strip()

# ==== File Upload Security ==== #
# Allowed file types and size limits
ALLOWED_SPRITE_TYPES = ["image/png", "image/jpeg"]
ALLOWED_AUDIO_TYPES = ["audio/mpeg", "audio/wav"]
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# ==== Upload Endpoints ==== #

# This POST endpoint is used to upload a sprite image to the database.
# 1. It accepts a file upload (only PNG or JPEG).
# 2. The file is validated for allowed content type and maximum size (5MB).
# 3. The filename is sanitized to avoid injection risks.
# 4. The file is Base64 encoded and saved in the 'Sprites' collection in MongoDB.
# 5. If successful, it returns a message with the inserted document's ID.
@app.post("/upload_sprite/", summary="Upload a sprite image", response_description="ID of the uploaded sprite")
async def upload_sprite(file: UploadFile = File(...)):
    try:
        db = get_db()
         # Check file type
        if file.content_type not in ALLOWED_SPRITE_TYPES:
            raise HTTPException(400, "Only PNG/JPEG images allowed")

        #Read and check file size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(400, "File exceeds 5MB limit")

        # Sanitize filename before storing
        clean_filename = sanitize_input(file.filename)
        
        #Convert to Base64 string
        encoded = base64.b64encode(content).decode("utf-8")

        # Create and insert document into Sprites collection
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
        await shutdown_db() # Ensure connection is closed

# This POST endpoint is used to upload an audio file.
# 1. It accepts an audio file (only MP3 or WAV).
# 2. Validates content type and file size just like the sprite upload.
# 3. The filename is sanitized for security.
# 4. The file is Base64 encoded and stored in the 'Audio' collection in MongoDB.
# 5. Responds with a message and the MongoDB ID of the stored audio.
@app.post("/upload_audio/", summary="Upload an audio file", response_description="ID of the uploaded audio")
async def upload_audio(file: UploadFile = File(...)):
    try:
        db = get_db()
        # Check allowed types
        if file.content_type not in ALLOWED_AUDIO_TYPES:
            raise HTTPException(400, "Only MP3/WAV audio allowed")

        # Check size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(400, "File exceeds 5MB limit")

        # Sanitize filname before storing
        clean_filename = sanitize_input(file.filename)
        
        # Convert to Base65 and insert into Audio collection
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

#This POST endpoint allows players to submit their name and score.
# 1. It uses a Pydantic model (PlayerScore) to validate inputs:
#    - Player name must be 1-50 characters long and only contain letters, numbers, spaces, or underscores.
# 2. The player name is sanitized using a regex function to prevent NoSQL injection.
# 3. The data is saved in the 'Scores' collection in MongoDB.
# 4. The server returns the inserted ID and a success message.
@app.post("/upload_score/", summary="Submit a player score", response_description="ID of the recorded score")
async def upload_score(score: PlayerScore):
    try:
        db = get_db()
        # Sanitize player name before storing
        sanitized_name = sanitize_input(score.player_name)
        
        # Create and insert score document
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

# This GET endpoint retrieves all uploaded sprite images from MongoDB.
# 1. It connects to the 'Sprites' collection and fetches all documents.
# 2. For each sprite, only the filename and description are returned (Base64 content is not shown).
# 3. Returns a JSON object with all sprite records.
@app.get("/get_sprites/")
async def get_sprites():
    try:
        db = get_db()
        cursor = db.Sprites.find()
        data = []
        # Loop through cursor and build response list
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

# This GET endpoint retrieves all audio files stored in the database.
# 1. It connects to the 'Audio' collection and gets all documents.
# 2. Returns the filename and description of each audio file.
# 3. Used to verify which audio assets have been uploaded.
@app.get("/get_audio/")
async def get_audio():
    try:
        db = get_db()
        cursor = db.Audio.find()
        data = []
        # Loop through cursor and build response list
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

# This GET endpoint returns all recorded player scores.
# 1. It connects to the 'Scores' collection in MongoDB.
# 2. Fetches all player score documents and returns them.
# 3. Each score includes the player's sanitized name and score value.
@app.get("/get_scores/")
async def get_scores():
    try:
        db = get_db()
        cursor = db.Scores.find()
        data = []
        # Loop through cursor and build response list
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