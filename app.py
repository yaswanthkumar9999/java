from fastapi import FastAPI, HTTPException, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4
from typing import Optional
import time
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI()

# Allow CORS for testing.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store.
sessions = {}

# Pydantic models.
class ChatPayload(BaseModel):
    model: str
    prompt: str
    category: str
    session_id:str

@app.get("/validate-key")
def validate_key(apiKey: str):
    # For testing, assume "my-secret-key" is valid.
    if apiKey == "sem":
        return {"message": "Valid API Key"}
    else:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@app.post("/stream-chat1")
def stream_chat1(payload: ChatPayload, response: Response, session_id: Optional[str] = Cookie(None)):
    params = payload.dict()
    print("params-->>",json.dumps(params))
    time.sleep(2)
    dummy_answer = f"Dummy answer for '{payload.prompt}' (model: {payload.model}, category: {payload.category})"
    if not session_id or session_id not in sessions:
        session_id = str(uuid4())
        sessions[session_id] = {"title": f"Session: {payload.prompt[:10]}...", "chats": []}
        response.set_cookie(key="session_id", value=session_id)
    sessions[session_id]["chats"].append({"prompt": payload.prompt, "answer": dummy_answer})
    print("yes")
    return "This is the answer"

@app.get("/history")
def get_history():
    history_list = []
    for session_id, data in sessions.items():
        history_list.append({"session_id": session_id, "title": data["title"]})
    return history_list

@app.get("/history/{session_id}")
def get_session_history(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]["chats"]

@app.delete("/history/{session_id}")
def delete_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
        return {"message": f"Session {session_id} deleted."}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

import random
@app.post("/save")
def save(payload:dict):
    print("payload-->>",payload)
    num = random.randint(1, 100)
    print("num-->>",num)
    id = num
    
    return {"status":"success","result":{"id":id,"timestamp":datetime.now()}}
@app.post("/feedback")
def feedback(payload:dict):
    print("payload-->>",payload)
    return "feedback saved successfully"




def generate_response(language: str):
    """Simulates an LLM response with streaming output."""
    if language.lower() == "python":
        response = [
            "### Introduction to Python\n",
            "- Python is a high-level, interpreted programming language.\n",
            "- It is known for its readability and simplicity.\n",
            "\n",
            "### Key Features\n",
            "- Dynamic typing and memory management.\n",
            "- Extensive standard library and third-party packages.\n",
            "- Used in web development, data science, AI, and more.\n",
            "\n",
            "### Sample Code\n",
            "```python\n",
            "def hello_world():\n",
            "    print(\"Hello, World!\")\n",
            "\n",
            "hello_world()\n",
            "```\n"
        ]
    elif language.lower() == "java":
        response = [
            "### Introduction to Java\n",
            "- Java is an object-oriented programming language.\n",
            "- It follows the Write Once, Run Anywhere (WORA) principle.\n",
            "\n",
            "### Key Features\n",
            "- Strongly typed language with garbage collection.\n",
            "- Platform-independent with JVM support.\n",
            "- Used in enterprise applications, Android development, and more.\n",
            "\n",
            "### Sample Code\n",
            "```java\n",
            "public class HelloWorld {\n",
            "    public static void main(String[] args) {\n",
            "        System.out.println(\"Hello, World!\");\n",
            "    }\n",
            "}\n",
            "```\n"
        ]
    else:
        response = ["### Error\n", "- Unsupported language. Please choose Python or Java.\n"]
    
    return response

async def stream_response(language: str):
    """Async generator that streams the response like an LLM."""
    response = generate_response(language)
    for chunk in response:
        yield chunk
        await asyncio.sleep(0.5)  # Simulate streaming delay

@app.post("/stream-chat")
def stream_chat(payload: ChatPayload, response: Response, session_id: Optional[str] = Cookie(None)):
    params = payload.dict()
    # print("params-->>",params)
    """Endpoint to stream the response for a given programming language."""
    return StreamingResponse(stream_response(params["prompt"]), media_type="text/plain")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
