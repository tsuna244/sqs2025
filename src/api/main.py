from typing import Union

from fastapi import FastAPI, Request, Depends, HTTPException, status

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from datetime import datetime, timedelta

from pydantic import BaseModel

from jose import jwt, JWTError

# imports all necessary custom modules
from .modules import PokemonObj, GenerationObj, Database

# authentication settings
SECRET_KEY = ""
ALGORITHM = "HS256"
ACESS_TOKEN_EXPIRE_MINUTES = 30


templates = Jinja2Templates(directory="api/templates")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    deck_ids: list[int]

oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth_2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW_Authenticate": "Bearer"})
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception
    
    user = Database.get_user(username, "")
    if user is None:
        raise credential_exception
    
    return user

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

app = FastAPI()
app.mount("/static", StaticFiles(directory="api/static"), name="static")


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(
        name="home.html",
        request=request
    )

# only page not function
@app.get("/login")
async def user_login_page(request: Request):
    return templates.TemplateResponse(
        name="login.html",
        request=request
    )

# only page not function
@app.get("/register")
async def user_registration_page(request: Request):
    return templates.TemplateResponse(
        name="register.html",
        request=request
    )

@app.post("/game", response_model=User)
async def game_page(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.post("/leaderboard")
async def leaderboard_page(current_user: User = Depends(get_current_active_user)):
    return current_user.deck_ids

@app.get("/Pokemon/{pokemon_id}")
async def read_pokemon(pokemon_id: int, request: Request):
    return PokemonObj(pokemon_id).__dict__().__str__()

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = Database.get_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW_Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}