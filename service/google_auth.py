from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from httpx import AsyncClient
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse

from service.common import create_access_token, get_current_user

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/v2/auth",
    tokenUrl="https://oauth2.googleapis.com/token"
)


async def login():
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id=1028999492610-ti0llh2pdtgm78hpi7bml67ukutn9p3v.apps.googleusercontent.com"
        f"&redirect_uri=http://localhost:8000/auth/callback"
        "&scope=openid%20email%20profile"
    )
    return RedirectResponse(google_auth_url)


async def auth_callback(request: Request):
    """
    Handle the callback from Google OAuth2.
        Parameters:
            request (Request): The request object.
        Returns:
            RedirectResponse: Redirects to the Swagger UI.
    """
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Authorization code not found.")

    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": "1028999492610-ti0llh2pdtgm78hpi7bml67ukutn9p3v.apps.googleusercontent.com",
        "client_secret": "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",
        "redirect_uri": "http://localhost:8000/auth/callback",
        "grant_type": "authorization_code",
    }
    async with AsyncClient() as client:
        token_response = await client.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_json = token_response.json()

    if "error" in token_json:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=token_json["error"])

    access_token = token_json["access_token"]
    userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with AsyncClient() as client:
        userinfo_response = await client.get(userinfo_url, headers=headers)
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()

    if "error" in userinfo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=userinfo["error"])

    jwt_token = create_access_token(data=userinfo)

    response = RedirectResponse(url="http://localhost:8000/docs")
    response.set_cookie(key="access_token", value=jwt_token, httponly=True)

    return response


async def protected(depends: dict = Depends(get_current_user)):
    return JSONResponse(depends)


async def logout():
    """
    Logout the user by deleting the access token cookie.
    """
    response = RedirectResponse(url="http://localhost:8080/swagger")
    response.delete_cookie("access_token")

    return response