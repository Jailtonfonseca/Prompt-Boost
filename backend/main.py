import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
import openai
from decouple import config
import database

# --- App Configuration ---
app = FastAPI(
    title="Prompt Enhancer API",
    description="An API to improve user-provided prompts using AI.",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    """Initialize the database on application startup."""
    database.init_db()

# --- CORS Configuration ---
# Allows requests from the frontend (assuming it runs on localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- Pydantic Models ---
class PromptRequest(BaseModel):
    prompt: str
    apiKey: str

class ImprovedPromptResponse(BaseModel):
    original_prompt: str
    improved_prompt: str

class ShareRequest(BaseModel):
    original_prompt: str
    improved_prompt: str

class ShareResponse(BaseModel):
    share_id: str

from typing import List

class PromptDetails(BaseModel):
    id: str
    original_prompt: str
    improved_prompt: str

class GalleryItem(BaseModel):
    id: str
    original_prompt: str
    improved_prompt: str

class GalleryResponse(BaseModel):
    prompts: List[GalleryItem]

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"status": "API is running"}

@app.post("/api/improve-prompt", response_model=ImprovedPromptResponse)
async def improve_prompt(request: PromptRequest):
    """
    Receives a prompt and an API key, improves the prompt using an AI model,
    and returns both the original and the improved prompts.
    """
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    if not request.apiKey:
        raise HTTPException(status_code=400, detail="API key is required.")

    try:
        # Configure the OpenAI client with the user-provided key
        client = openai.OpenAI(api_key=request.apiKey)

        # The instruction for the AI model to improve the prompt
        enhancement_instruction = (
            "Please refine the following user prompt to be more clear, focused, and effective. "
            "Preserve the original intent and key elements, but enhance its structure and wording "
            "to yield better results from an AI model. Here is the user's prompt:"
        )

        # Make the API call to OpenAI
        completion = client.chat.completions.create(
            model="gpt-4o",  # Using the latest model as requested
            messages=[
                {"role": "system", "content": enhancement_instruction},
                {"role": "user", "content": request.prompt}
            ]
        )

        improved_prompt_text = completion.choices[0].message.content.strip()

        return ImprovedPromptResponse(
            original_prompt=request.prompt,
            improved_prompt=improved_prompt_text
        )

    except openai.AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid OpenAI API key.")
    except Exception as e:
        # Catch other potential exceptions (e.g., network issues, invalid requests)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.post("/api/prompts", response_model=ShareResponse)
async def share_prompt(request: ShareRequest):
    """Saves a prompt pair and returns a unique ID for sharing."""
    if not request.original_prompt or not request.improved_prompt:
        raise HTTPException(status_code=400, detail="Both prompts must be provided.")

    try:
        share_id = database.save_prompt(request.original_prompt, request.improved_prompt)
        return ShareResponse(share_id=share_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save prompt: {str(e)}")

@app.get("/api/prompts/{prompt_id}", response_model=PromptDetails)
async def get_shared_prompt(prompt_id: str):
    """Retrieves a shared prompt pair by its ID."""
    prompt = database.get_prompt(prompt_id)
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found.")
    return PromptDetails(
        id=prompt['id'],
        original_prompt=prompt['original_prompt'],
        improved_prompt=prompt['improved_prompt']
    )

@app.post("/api/prompts/{prompt_id}/publish", status_code=204)
async def publish_shared_prompt(prompt_id: str):
    """Marks a specific prompt as public."""
    prompt = database.get_prompt(prompt_id)
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found.")

    try:
        database.publish_prompt(prompt_id)
        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish prompt: {str(e)}")

@app.get("/api/gallery", response_model=GalleryResponse)
async def get_gallery():
    """Retrieves all prompts that have been made public."""
    try:
        prompts = database.get_public_prompts()
        return GalleryResponse(prompts=[GalleryItem(**dict(p)) for p in prompts])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve gallery: {str(e)}")

# --- To run the app locally: uvicorn main:app --reload ---
