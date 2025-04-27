from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import httpx
import os

app = FastAPI()

# Load API keys from environment variables for security
VAPI_API_KEY = os.getenv("VAPI_API_KEY", "")
RETELL_API_KEY = os.getenv("RETELL_API_KEY", "")

class AgentCreateRequest(BaseModel):
    provider: str  # "vapi" or "retell"
    common_params: Dict[str, Any]

def map_to_vapi_params(common_params: Dict[str, Any]) -> Dict[str, Any]:
    # Map common parameters to Vapi API parameters
    vapi_params = {
        "name": common_params.get("name"),
        "firstMessage": common_params.get("first_message"),
        "model": common_params.get("model"),
        "voice": common_params.get("voice"),
        # Add more mappings as needed
    }
    # Remove None values
    return {k: v for k, v in vapi_params.items() if v is not None}

def map_to_retell_params(common_params: Dict[str, Any]) -> Dict[str, Any]:
    # Map common parameters to Retell API parameters
    retell_params = {
        "agent_name": common_params.get("name"),
        "response_engine": common_params.get("response_engine"),
        "voice_id": common_params.get("voice_id"),
        # Add more mappings as needed
    }
    # Remove None values
    return {k: v for k, v in retell_params.items() if v is not None}

@app.post("/create-agent")
async def create_agent(request: AgentCreateRequest):
    if request.provider not in ["vapi", "retell"]:
        raise HTTPException(status_code=400, detail="Invalid provider. Must be 'vapi' or 'retell'.")

    if request.provider == "vapi":
        if not VAPI_API_KEY:
            raise HTTPException(status_code=500, detail="VAPI_API_KEY not set in environment variables")
        headers = {
            "Authorization": f"Bearer {VAPI_API_KEY}",
            "Content-Type": "application/json"
        }
    else:
        if not RETELL_API_KEY:
            raise HTTPException(status_code=500, detail="RETELL_API_KEY not set in environment variables")
        headers = {
            "Authorization": f"Bearer {RETELL_API_KEY}",
            "Content-Type": "application/json"
        }

    async with httpx.AsyncClient() as client:
        if request.provider == "vapi":
            url = "https://api.vapi.ai/assistant"
            payload = map_to_vapi_params(request.common_params)
            response = await client.post(url, json=payload, headers=headers)
        else:  # retell
            url = "https://api.retellai.com/create-agent"
            payload = map_to_retell_params(request.common_params)
            response = await client.post(url, json=payload, headers=headers)

    if response.status_code not in [200, 201]:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()
