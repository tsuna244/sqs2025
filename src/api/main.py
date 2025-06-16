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
ACESS_TOKEN_EXPIRE_MINUTES = 15

db = None

if os.environ.get("TEST", 'Not Set') != "1":
    db = Database()
    db.create_table()
    templates = Jinja2Templates(directory="api/templates")
    if os.environ.get("TEST", 'Not Set') == "2":
        db.add_user("testuser", "Asdf1234", [])
else:
    templates = Jinja2Templates(directory=os.path.abspath("src/api/templates"))

gen_1 = GenerationObj(1)
gen_2 = GenerationObj(2)
gen_3 = GenerationObj(3)

def create_db(db_settings):
    """Test function that creates a db object for testing with the given settings. only works if TEST env var is set

    :param db_settings: settings for the test db connection
    :type db_settings: dict
    :raises ImportError: raises error if not in test mode
    """
    if os.environ.get("TEST", 'Not Set') != "1":
        raise ImportError("This function is only for testing purposes")
    global db
    db = Database(db_settings)
    db.create_table()
    db.clean_table()

def close_db():
    """Test function to close the test db. only works if TEST env var is set

    :raises ImportError: raises error if not in test mode
    """
    if os.environ.get("TEST", 'Not Set') != "1":
        raise ImportError("This function is only for testing purposes")
    global db
    db.close()

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    expires: float

class User(BaseModel):
    user_id: int
    user_name: str
    deck_ids: list
    points: int

class RegistrationModel(BaseModel):
    username: str
    password: str

class AddDeckModel(BaseModel):
    username: str
    new_elem: dict

class AddPointsModel(BaseModel):
    username: str
    points_elem: int

oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Creates an access token using the data and an expiring time in minutes

    :param data: dictionary containing data to include in the access token
    :type data: dict
    :param expires_delta: time in Minutes the token expires in, defaults to None
    :type expires_delta: timedelta | None, optional
    :return: jwt token
    :rtype: str
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth_2_scheme)):
    """fetches the user from the given token and authorizes him

    :param token: the jwt token str, defaults to Depends(oauth_2_scheme)
    :type token: str, optional
    :raises credential_exception: raises if username inside the token is none
    :raises credential_exception: raises if JWT Error occures
    :raises credential_exception: raises if user id is -1
    :raises credential_exception: raises if expiration date is not set
    :raises credential_exception: raises if token is expired
    :return: User object containg user information: user_id, user_name, deck_ids list and points
    :rtype: User
    """
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
    
    return User(user_id=user["user_id"], user_name=user["user_name"], deck_ids=user["deck_ids"], points=user["points"])

app = FastAPI()
app.mount("/static", StaticFiles(directory="api/static"), name="static")


@app.get("/")
async def read_root(request: Request):
    """Api call: root "/" home page.

    :param request: the get request
    :type request: Request
    :return: html response with parsed home.html
    :rtype: jinja TemplateResponse
    """
    return templates.TemplateResponse(
        name="home.html",
        request=request
    )

# only page not function
@app.get("/login")
async def user_login_page(request: Request):
    """Api call: login page "/login"

    :param request: the get request
    :type request: Request
    :return: html response with parsed login.html
    :rtype: jinja TemplateResponse
    """
    return templates.TemplateResponse(
        name="login.html",
        request=request
    )

# only page not function
@app.get("/register")
async def user_registration_page(request: Request):
    """Api call: register page "/register"

    :param request: the get request
    :type request: Request
    :return: html response with parsed register.html
    :rtype: jinja TemplateResponse
    """
    return templates.TemplateResponse(
        name="register.html",
        request=request
    )

err_dict_user = {"details": "Input error! Username must be alpha only"}

@app.post("/register_user")
async def register_new_user(request: RegistrationModel):
    """Api call: Post request to register a new user

    :param request: contains information to register a new user: username, password
    :type request: RegistrationModel
    :return: dict containing information about the registration: {"details": msg: str}
    :rtype: dict
    """
    # TODO: change to alpha numeric for username
    if not isinstance(request.username, str) or not request.username.isalpha():
        return err_dict_user
    if not isinstance(request.password, str) or not request.password.isascii():
        return {"details": "Input error! Password must be ascii chars only"}
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
    """API call: returns and authenticates a user

    :param current_user: will be retrieved from the token inside of authentication header, defaults to Depends(get_current_user)
    :type current_user: User, optional
    :return: the user of the token inside the header
    :rtype: User
    """
    return current_user

@app.post("/get_users")
async def get_users():
    """Api call: returns a dict with all users

    :return: list with all users inside of dict: {"users": [{...}, {...}]}
    :rtype: dict
    """
    return db.get_users()

@app.get("/leaderboard")
async def leaderboard_page(request: Request):
    """Api call: leaderboard page "/leaderboard"

    :param request: the get request
    :type request: Request
    :return: html response with parsed leaderboard.html
    :rtype: jinja TemplateResponse
    """
    return templates.TemplateResponse(
        name="leaderboard.html",
        request=request
    )

@app.get("/my_deck")
async def my_deck_page(request: Request):
    """Api call: My Deck page "/my_deck"

    :param request: the get request
    :type request: Request
    :return: html response with parsed mydeck.html
    :rtype: jinja TemplateResponse
    """
    return templates.TemplateResponse(
        name="mydeck.html",
        request=request
    )

@app.get("/pack_opening")
async def get_pack_opening(request: Request):
    """Api call: Pack opening page "/pack_opening"

    :param request: the get request
    :type request: Request
    :return: html response with parsed pack.html
    :rtype: jinja TemplateResponse
    """
    return templates.TemplateResponse(
        name="pack.html",
        request=request
    )

@app.get("/unauth")
async def unauthorized_access(request: Request):
    """Api call: Unauthorized page "/unauth"

    :param request: the get request
    :type request: Request
    :return: html response with parsed unauth.html
    :rtype: jinja TemplateResponse
    """
    return templates.TemplateResponse(
        name="unauth.html",
        request=request
    )

if os.environ.get("TEST", 'Not Set') == "2":

    test_pokemon = {'pokemon_id': 132, 'pokemon_name': 'ditto', 'pokemon_generation': 'generation-i', 'pokemon_rarity': 'normal', 'pokemon_points': 48, 'pokemon_stats': [{'stat_name': 'hp', 'stat_value': 48}, {'stat_name': 'attack', 'stat_value': 48}, {'stat_name': 'defense', 'stat_value': 48}, {'stat_name': 'special-attack', 'stat_value': 48}, {'stat_name': 'special-defense', 'stat_value': 48}, {'stat_name': 'speed', 'stat_value': 48}], 'pokemon_sprite_path': ''}

    @app.post("/Pokemon_Id/{pokemon_id}")
    async def read_pokemon(pokemon_id: int, request: Request):
        return test_pokemon # TODO: return pokemon object as dict (example)

    @app.post("/Pokemon_Name/{pokemon_name}")
    async def get_pokemon_by_name(pokemon_name:str, request: Request):
        return test_pokemon

    @app.post("/Pokemon_Rand/{gen_id}")
    async def get_random_pokemon_from_gen(gen_id: int, request: Request):
        if gen_id == 1 or gen_id == 2 or gen_id == 3:
            return test_pokemon # TODO: return pokemon object as dict (example)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Only generation 1 to 3 are supported")
else:
    @app.post("/Pokemon_Id/{pokemon_id}")
    async def read_pokemon(pokemon_id: int, request: Request):
        """Api call: Post request to retrieve a pokemon by id

        :param pokemon_id: id of the pokemon
        :type pokemon_id: int
        :param request: the get request
        :type request: Request
        :return: PokemonObj in form of a dictionary
        :rtype: dict
        """
        return PokemonObj(pokemon_id).__dict__()

    @app.post("/Pokemon_Name/{pokemon_name}")
    async def get_pokemon_by_name(pokemon_name:str, request: Request):
        """Api call: Post request to retrive a pokemon by name

        :param pokemon_name: the name of the pokemon
        :type pokemon_name: str
        :param request: the get request
        :type request: Request
        :return: PokemonObj in form of a dictionary
        :rtype: dict
        """
        pokemon = PokemonObj.from_pokemon_name(pokemon_name)
        if isinstance(pokemon, dict):
            return pokemon
        else:
            print(pokemon.__dict__())
            return pokemon.__dict__()

    @app.post("/Pokemon_Rand/{gen_id}")
    async def get_random_pokemon_from_gen(gen_id: int, request: Request):
        """Api call: Post request to retrieve a random pokemon of a given generation (1-3)

        :param gen_id: the id of the generation (1-3 are supported only)
        :type gen_id: int
        :param request: the get Request
        :type request: Request
        :raises HTTPException: raises if the generation is not 1-3
        :return: PokemonObj in form of a dictionary
        :rtype: dict
        """
        if gen_id == 1:
            return gen_1.get_random_pokemon().__dict__()
        elif gen_id == 2:
            return gen_2.get_random_pokemon().__dict__()
        elif gen_id == 3:
            return gen_3.get_random_pokemon().__dict__()
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Only generation 1 to 3 are supported")

err_dict = {"details": "Error occured! Did not add element to user"}

@app.post("/add_to_deck")
async def add_elem_to_user_deck(request: AddDeckModel):
    """Api call: Post request to add an element to the deck of a user

    :param request: json body containing the username and the new element (dict) that will be added to the user
    :type request: AddDeckModel
    :return: dictionary contaiing details of the result: {"details": msg_str}
    :rtype: dict
    """
    if not isinstance(request.username, str) or not request.username.isalpha():
        return err_dict_user
    if not isinstance(request.new_elem, dict):
        return err_dict
    if db.add_elem_to_user_deck(request.username, request.new_elem) != 0:
        return err_dict
    else:
        return {"details": "New element got added to user"}

@app.post("/update_points")
async def update_points_of_user(request: AddPointsModel):
    """Api call: Post request to update the points of a user

    :param request: json body containing the username and the points (int) that will be updated
    :type request: AddDeckModel
    :return: dictionary contaiing details of the result: {"details": msg_str}
    :rtype: dict
    """
    if not isinstance(request.username, str) or not request.username.isalpha():
        return err_dict_user
    if not isinstance(request.points_elem, int) or request.points_elem < 0:
        return {"details": "Input error! Point elem must be positive integer"}
    if db.update_user_points(request.username, request.points_elem) != 0:
        return err_dict
    return {"details": "Added points to user successfully"}

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Api call: Post request to generate a token with login credentials: username, password

    :param form_data: login form containing username and password, defaults to Depends()
    :type form_data: OAuth2PasswordRequestForm, optional
    :raises HTTPException: raises if authentication fails
    :return: dict containing token and type: {"access_token": token, "token_type": type}
    :rtype: dict
    """
    user = db.authenticate_user(form_data.username, form_data.password)
    if user["user_id"] == -1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW_Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["user_name"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}