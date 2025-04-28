import base64
import os
import re
import threading
import urllib.parse
from typing import Annotated

import fastapi
from fastapi import FastAPI, Request, Response, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=base64.b64encode(os.urandom(64)).decode())
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://donations.challs.umdctf.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


users = {
    "lisanalgaib": {
        "username": "lisanalgaib",
        "password": base64.b64encode(os.urandom(64)).decode(),
        "url": "https://imageio.forbes.com/specials-images/imageserve/5bb22ae84bbe6f67d2e82e05/0x0.jpg?format=jpg&crop=1012,1013,x627,y129,safe&height=416&width=416&fit=bounds",
        "currency": 1_000
    }
}
lock = threading.Lock()


@app.post("/api/login")
async def login(request: Request, content_type: Annotated[str | None, Header()] = None):
    if content_type != "application/x-www-form-urlencoded":
        raise HTTPException(status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                            detail="Content-Type must be application/x-www-form-urlencoded")

    request_body = (await request.body()).decode()
    params = dict(urllib.parse.parse_qsl(request_body))
    if "username" not in params:
        raise HTTPException(status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="username is missing")
    if "password" not in params:
        raise HTTPException(status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="password is missing")

    with lock:
        if params["username"] not in users:
            raise HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN, detail="user does not exist")

        if params["password"] != users[params["username"]]["password"]:
            raise HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN, detail="invalid password")

        request.session["username"] = params["username"]

    return Response(status_code=fastapi.status.HTTP_200_OK, content="successfully logged in")


@app.post("/api/register")
async def register(request: Request, content_type: Annotated[str | None, Header()] = None):
    if content_type != "application/x-www-form-urlencoded":
        raise HTTPException(status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                            detail="Content-Type must be application/x-www-form-urlencoded")

    request_body = (await request.body()).decode()
    print(request_body)
    params = dict(urllib.parse.parse_qsl(request_body))
    print(params)
    if "username" not in params:
        raise HTTPException(status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="username is missing")
    if "password" not in params:
        raise HTTPException(status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="password is missing")

    with lock:
        if params["username"] in users:
            raise HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN, detail="user already exists")

        users[params["username"]] = {
            "username": params["username"],
            "password": params["password"],
            "url": None,
            "currency": 1_000
        }

    return Response(status_code=fastapi.status.HTTP_200_OK, content="successfully registered")


@app.get("/api/user")
async def info(username: str):
    with lock:
        if username not in users:
            raise HTTPException(status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="user does not exist")

        user = users[username].copy()
        del user["password"]
        return user


@app.post("/api/donate")
async def donate(request: Request, content_type: Annotated[str | None, Header()] = None):
    if content_type != "application/x-www-form-urlencoded":
        raise HTTPException(status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                            detail="Content-Type must be application/x-www-form-urlencoded")

    if "username" not in request.session:
        raise HTTPException(status_code=fastapi.status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

    request_body = (await request.body()).decode()
    if not re.search("^to=lisanalgaib&|&to=lisanalgaib$|&to=lisanalgaib&", request_body):
        raise HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN, detail="you may only donate to Jeff Bezos")

    params = dict(urllib.parse.parse_qsl(request_body))
    if "currency" not in params:
        raise HTTPException(status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="currency is missing")

    currency = int(params["currency"])

    if "to" not in params:
        raise HTTPException(status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="to is missing")

    with lock:
        if request.session["username"] not in users:
            request.session.pop("username")
            raise HTTPException(status_code=fastapi.status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

        from_user = users[request.session["username"]]
        if from_user["currency"] < currency:
            raise HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN, detail="you're too poor")

        if params["to"] not in users:
            raise HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN, detail="invalid user")

        to_user = users[params["to"]]
        from_user["currency"] -= currency
        to_user["currency"] += currency

    return Response(status_code=fastapi.status.HTTP_200_OK, content="thank you for your contribution")


@app.get("/api/flag")
async def flag(request: Request):
    if "username" not in request.session:
        raise HTTPException(status_code=fastapi.status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

    with lock:
        if request.session["username"] not in users:
            request.session.pop("username")
            raise HTTPException(status_code=fastapi.status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

        user = users[request.session["username"]]
        if user["currency"] < 5_000:
            raise HTTPException(status_code=fastapi.status.HTTP_403_FORBIDDEN,
                                detail="only the wealthy may view the treasure...")

        return Response(status_code=fastapi.status.HTTP_200_OK, content="UMDCTF{BE20$_1s_7h3_T0N6U3_OF_Th3_uN5e3N}")
