import os
import requests
import uuid
from pathlib import Path
from openai import OpenAI
from config import BASE_DIR

# Ensure a dedicated folder for generated images exists
IMAGE_SAVE_DIR = BASE_DIR / "static" / "generated_images"
IMAGE_SAVE_DIR.mkdir(parents=True, exist_ok=True)

def generate_image(prompt: str) -> str:
    """
    Generates a high-quality picture using DALL-E 3 on OpenAI.
    Saves it locally and returns the relative path for the frontend.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or "sk-proj" not in api_key:
        return "Error: OpenAI API Key is missing or invalid. Please add it to your .env file to create pictures."

    try:
        client = OpenAI(api_key=api_key)
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url
        
        # Download and save the image locally
        filename = f"gen_{uuid.uuid4().hex[:8]}.png"
        filepath = IMAGE_SAVE_DIR / filename
        
        img_data = requests.get(image_url).content
        with open(filepath, 'wb') as handler:
            handler.write(img_data)
            
        # Return path relative to the static folder (for frontend serving)
        relative_path = f"/static/generated_images/{filename}"
        return f"🎨 Picture Created! Saved locally. [IMAGE: {relative_path}]"

    except Exception as e:
        return f"Error generating picture: {str(e)}"
