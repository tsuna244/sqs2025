from typing import Union

from fastapi import FastAPI, Request

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel

# imports all necessary custom modules
from .modules import PokemonObj, GenerationObj


templates = Jinja2Templates(directory="app/templates")


app = FastAPI()
app.mount("/static", StaticFiles(directory="api/static"), name="static")


@app.get("/")
async def read_root(request: Request):
    return {"Test": "Test"}


@app.get("/Pokemon/{pokemon_id}")
async def read_pokemon(pokemon_id: int, request: Request):
    return PokemonObj(pokemon_id).__dict__().__str__()
