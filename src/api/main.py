from typing import Union

from fastapi import FastAPI, Request, Depends, HTTPException, status

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from datetime import datetime, timedelta

from pydantic import BaseModel

from jose import jwt, JWTError
import os

# imports all necessary custom modules
from .modules import PokemonObj, GenerationObj, Database

# authentication settings
SECRET_KEY = "verysecretkey"
ALGORITHM = "HS256"
ACESS_TOKEN_EXPIRE_MINUTES = 1

db = None

if os.environ.get("TEST", 'Not Set') != "1":
    db = Database()

def create_db(db_settings):
    return Database(db_settings)
if os.environ.get("TEST", 'Not Set') != "1":
    templates = Jinja2Templates(directory="api/templates")
else:
    templates = Jinja2Templates(directory="../api/templates")
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    expires: float

class User(BaseModel):
    user_id: int
    user_name: str
    deck_ids: list[int]

class RegistrationModel(BaseModel):
    username: str
    password: str

oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth_2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW_Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        expires = payload.get("exp")
        if username is None:
            raise credential_exception
        token_data = TokenData(username=username, expires=expires)
    except JWTError:
        raise credential_exception
    
    user = db.get_user(token_data.username)
    if user["user_id"] == -1:
        raise credential_exception
    
    if expires is None:
        raise credential_exception
    if datetime.now().timestamp() > token_data.expires:
        raise credential_exception
    
    return User(user_id=user["user_id"], user_name=user["user_name"], deck_ids=user["deck_ids"])

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

@app.post("/register_user")
async def register_new_user(request: RegistrationModel):
    result = db.add_user(request.username, request.password, [])
    if result == 0:
        # check inside registration if user already exists in db!!!
        return {"details": f"User {request.username} successfully registered"}
    elif result == 3:
        return {"details": f"UnuiqeViolation! User {request.username} already exists"}
    elif result == 1:
        return {"details": "Connection error! Could not register user! Connection to database failed!"}
    else:
        return {"details": "Database Error! Could not register user! Unhandeled Error occured"}

@app.post("/get_user", response_model=User)
async def get_user(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/leaderboard")
async def leaderboard_page():
    return {"TBD": "TBD"}

@app.get("/my_deck")
async def my_deck_page():
    return {"TBD": "TBD"}

@app.get("/pack_opening")
async def get_pack_opening():
    return {"TBD": "TBD"}

@app.post("/Pokemon_Id/{pokemon_id}")
async def read_pokemon(pokemon_id: int, request: Request):
    return PokemonObj(pokemon_id).__dict__()

@app.post("/Pokemon_Name/{pokemon_name}")
async def get_pokemon_by_name(pokemon_name:str, request: Request):
    pokemon = PokemonObj.from_pokemon_name(pokemon_name)
    if isinstance(pokemon, dict):
        return pokemon
    else:
        return pokemon.__dict__()

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.authenticate_user(form_data.username, form_data.password)
    if user["user_id"] == -1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW_Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["user_name"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}