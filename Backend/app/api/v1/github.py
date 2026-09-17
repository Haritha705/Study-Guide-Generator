from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
import httpx
from app.config import settings

router = APIRouter()

@router.get("/login")
async def github_login():
    """Redirect to GitHub OAuth authorization page."""
    if not settings.GITHUB_OAUTH_CLIENT_ID:
        raise HTTPException(status_code=500, detail="GitHub OAuth not configured")
        
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_OAUTH_CLIENT_ID}"
        f"&redirect_uri={settings.GITHUB_OAUTH_REDIRECT_URI}"
        f"&scope=repo,read:user"
    )
    return RedirectResponse(url=github_auth_url)

@router.get("/callback")
async def github_callback(code: str):
    """Handle GitHub OAuth callback and exchange code for access token."""
    if not code:
        raise HTTPException(status_code=400, detail="No authorization code provided")
        
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.GITHUB_OAUTH_CLIENT_ID,
                "client_secret": settings.GITHUB_OAUTH_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GITHUB_OAUTH_REDIRECT_URI,
            }
        )
        
        data = response.json()
        if "error" in data:
            raise HTTPException(status_code=400, detail=data.get("error_description", "OAuth failed"))
            
        access_token = data.get("access_token")
        
        # Redirect back to frontend with the token
        frontend_url = settings.FRONTEND_URL.rstrip("/")
        if access_token:
            return RedirectResponse(url=f"{frontend_url}/?github_token={access_token}")
        else:
            return RedirectResponse(url=f"{frontend_url}/?github_error=NoToken")


from pydantic import BaseModel
from app.services.mcp_client import mcp_client

class GitHubExtractRequest(BaseModel):
    repo: str
    path: str
    github_token: str

import base64

@router.post("/extract")
async def extract_github_file(req: GitHubExtractRequest):
    try:
        if "/" not in req.repo:
            raise HTTPException(status_code=400, detail="Repository must be in format 'owner/repo'")
            
        owner, repo_name = req.repo.split("/", 1)
        
        result = await mcp_client.call_tool(
            "github_get_file_content",
            {"owner": owner, "repo": repo_name, "path": req.path},
            token=req.github_token
        )
        
        # Parse MCP response structure
        file_content = result.get("content", [])
        if not file_content:
            raise ValueError("No content returned from GitHub")
            
        base64_data = file_content[0].get("text", "")
        
        # Decode the base64 content
        try:
            decoded_text = base64.b64decode(base64_data).decode("utf-8")
        except Exception as decode_err:
            raise ValueError(f"Failed to decode file content (may be binary): {decode_err}")
            
        return {"extracted_text": decoded_text}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch GitHub file: {e}")
