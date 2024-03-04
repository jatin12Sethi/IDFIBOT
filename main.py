# import fastapi
# import embedchain
import os
# from embedchain import App
from fastapi import FastAPI
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from time import sleep
import uvicorn
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set this to your React app's URL in a production environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise HTTPException("OPENAI_API_KEY environment variable is not set")

client = OpenAI(api_key=OPENAI_API_KEY)

# Create or load assistant
assistant_id = "asst_pFiUM3oJWEekT7rDosegeThC"

# Root route
@app.get("/")
async def read_root():
    return {"message": "🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀"}


class DialogueSnippet(BaseModel):
    thread_id: str
    message: str


# Start conversation thread
@app.get("/start")
async def start_conversation():
    print("Starting a new conversation...")  # Debugging line
    thread = client.beta.threads.create()
    print(f"New thread created with ID: {thread.id}")  # Debugging line
    return {"thread_id": thread.id}


# Generate response
@app.post("/chat")
async def chat(dialogueSnippet: DialogueSnippet):
    dialogue = dialogueSnippet.dict()
    thread_id = dialogue.get("thread_id")
    user_input = dialogue.get("message", "")

    if not thread_id:
        print("Error: Missing thread_id")  # Debugging line
        return {"error": "Missing thread_id"}, 400

    print(
        f"Received message: {user_input} for thread ID: {thread_id}"
    )  # Debugging line

    # Add the user's message to the thread
    client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=user_input
    )

    # Run the Assistant
    run = client.beta.threads.runs.create(
        thread_id=thread_id, assistant_id=assistant_id
    )

    # Check if the Run requires action (function call)
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread_id, run_id=run.id
        )
        print(f"Run status: {run_status.status}")
        if run_status.status == "completed":
            break
        sleep(1)  # Wait for a second before checking again

    # Retrieve and return the latest message from the assistant
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    response = messages.data[0].content[0].text.value

    print(f"Assistant response: {response}")  # Debugging line
    return {"response": response}