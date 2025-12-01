import fastapi
from routers import characters, spells, items
from dotenv import load_dotenv
import os
import openai
from routers.characters import router as character_router

load_dotenv()
app = fastapi.FastAPI()

app.include_router(character_router)

apikey = os.getenv("apikey")


@app.get("/")
async def root():
    return {"message": f"Welcome to the DnD Character Tool API {apikey}"}


@app.get("/character-creation")
async def character_creation():
    return {"message": "Character creation endpoint"}


@app.get("/agent-call/")
async def agent_call():
    client = openai.OpenAI(api_key=apikey)

    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": "Hello, world! Please respond with a short greeting.",
            }
        ],
        max_tokens=50,
    )

    message = resp.choices[0].message.content.strip()
    return {"message": message}
