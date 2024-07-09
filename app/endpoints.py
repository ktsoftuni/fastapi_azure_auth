import uvicorn
from fastapi import Depends, FastAPI
from starlette.requests import Request

from service.common import get_current_user
from service.google_auth import auth_callback, login, logout

app = FastAPI()


@app.get("/login")
async def login_route():
    return await login()


@app.get("/auth/callback")
async def auth_callback_route(request: Request):
    return await auth_callback(request)



@app.get("/protected")
async def protected_route(current_user=Depends(get_current_user)):
    return current_user



@app.get("/logout")
async def logout_route():
    return await logout()



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)