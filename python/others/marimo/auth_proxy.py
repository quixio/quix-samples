"""
Auth proxy service for Quix plugin integration.
Handles postMessage token exchange and validates tokens against Quix API.
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Response, Cookie
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional

app = FastAPI()

# In-memory session store (tokens are short-lived anyway)
# Maps session_id -> {token: str, expires: datetime}
sessions: dict = {}

# Session cookie name
SESSION_COOKIE = "quix_session"
SESSION_DURATION_HOURS = 8

# Quix API configuration
PORTAL_API = os.environ.get("Quix__Portal__Api", "")
WORKSPACE_ID = os.environ.get("Quix__Workspace__Id", "")


def validate_quix_token(token: str) -> bool:
    """Validate token against Quix API."""
    if not token:
        print("Token validation failed: No token provided")
        return False

    # Log environment for debugging
    print(f"Validating token against Quix API")
    print(f"PORTAL_API: {PORTAL_API}")
    print(f"WORKSPACE_ID: {WORKSPACE_ID}")

    try:
        from quixportal.auth import Auth
        auth = Auth()
        # Validate that the user has read access to this workspace
        result = auth.validate_permissions(
            token=token,
            resourceType="Workspace",
            resourceID=WORKSPACE_ID,
            permissions="Read"
        )
        print(f"Token validation result: {result}")
        return bool(result)
    except Exception as e:
        print(f"Token validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_session(token: str) -> str:
    """Create a new session for a validated token."""
    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = {
        "token": token,
        "expires": datetime.utcnow() + timedelta(hours=SESSION_DURATION_HOURS)
    }
    # Clean up old sessions
    cleanup_sessions()
    return session_id


def cleanup_sessions():
    """Remove expired sessions."""
    now = datetime.utcnow()
    expired = [sid for sid, data in sessions.items() if data["expires"] < now]
    for sid in expired:
        del sessions[sid]


def is_valid_session(session_id: str) -> bool:
    """Check if session is valid and not expired."""
    if not session_id or session_id not in sessions:
        return False
    session = sessions[session_id]
    if session["expires"] < datetime.utcnow():
        del sessions[session_id]
        return False
    return True


# HTML page that handles postMessage token exchange
AUTH_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Authenticating...</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: #1a1a2e;
            color: #eee;
        }
        .container {
            text-align: center;
        }
        .spinner {
            width: 40px;
            height: 40px;
            border: 3px solid #333;
            border-top-color: #6366f1;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .error {
            color: #f87171;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="spinner"></div>
        <p id="status">Authenticating with Quix...</p>
        <p id="error" class="error"></p>
    </div>
    <script>
        let tokenReceived = false;

        // Listen for auth token from parent
        window.addEventListener('message', async function(event) {
            // Validate origin if needed
            if (event.data && event.data.type === 'AUTH_TOKEN' && event.data.token) {
                tokenReceived = true;
                document.getElementById('status').textContent = 'Validating token...';

                try {
                    const response = await fetch('/validate-token', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ token: event.data.token })
                    });

                    if (response.ok) {
                        // Token validated, cookie set - redirect to app
                        window.location.href = '/';
                    } else {
                        const data = await response.json();
                        showError(data.detail || 'Token validation failed');
                    }
                } catch (e) {
                    showError('Failed to validate token: ' + e.message);
                }
            }
        });

        // Request token from parent
        if (window.parent !== window) {
            window.parent.postMessage({ type: 'REQUEST_AUTH_TOKEN' }, '*');
        } else {
            showError('This application must be accessed through Quix Portal');
        }

        // Timeout if no token received
        setTimeout(function() {
            if (!tokenReceived) {
                showError('No authentication token received from Quix Portal');
            }
        }, 10000);

        function showError(msg) {
            document.getElementById('status').style.display = 'none';
            document.querySelector('.spinner').style.display = 'none';
            document.getElementById('error').textContent = msg;
            document.getElementById('error').style.display = 'block';
        }
    </script>
</body>
</html>
"""


@app.get("/auth", response_class=HTMLResponse)
async def auth_page():
    """Serve the authentication page that handles postMessage token exchange."""
    return AUTH_PAGE_HTML


@app.post("/validate-token")
async def validate_token(request: Request, response: Response):
    """Validate a Quix token and create a session."""
    try:
        data = await request.json()
        token = data.get("token")

        if not token:
            return JSONResponse({"detail": "No token provided"}, status_code=400)

        if validate_quix_token(token):
            session_id = create_session(token)
            response = JSONResponse({"status": "ok"})
            response.set_cookie(
                key=SESSION_COOKIE,
                value=session_id,
                httponly=True,
                secure=True,
                samesite="none",  # Required for iframe
                max_age=SESSION_DURATION_HOURS * 3600
            )
            return response
        else:
            return JSONResponse({"detail": "Invalid token"}, status_code=401)
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)


@app.get("/internal-auth")
async def internal_auth(request: Request, quix_session: Optional[str] = Cookie(None, alias=SESSION_COOKIE)):
    """Internal endpoint for nginx auth_request - returns 200 if authenticated, 401 if not."""
    if is_valid_session(quix_session):
        return Response(status_code=200)
    # Return 401 - nginx will redirect to /auth
    return Response(status_code=401)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8082)
