from typing import Union

from fastapi import FastAPI, Request

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel

from pokeapi import *

templates = Jinja2Templates(directory="app/templates")


app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def read_root(request: Request):
    return {"Test": "Test"}

@app.get("/pokesprite")
async def read_item(request: Request):
    return templates.TemplateResponse(
        name="base.html",
        request=request, 
        context={"brand": get_pokesprite_url_by_id(69)}
    )