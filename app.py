from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
from agent_group import AgentGroup


class ChatRequest(BaseModel):
    session_id: str
    message: str


app = FastAPI()
sessions: Dict[str, AgentGroup] = {}


@app.post("/chat")
def chat(request: ChatRequest):
    session_id = request.session_id
    message = request.message
    if session_id not in sessions.keys():
        sessions[session_id] = AgentGroup()
    agent_group = sessions[session_id]
    reply = agent_group.process_user_message(message)
    return {"reply": reply, "status": "success"}
