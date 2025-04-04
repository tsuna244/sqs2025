from typing import Union

from fastapi import FastAPI, Request

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel

from pokeapi import *

from postgresql import *

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

@app.get("/test_postgresql")
async def create_postgres_test(request: Request):
    conn = get_postgress_conn()
    
    if conn is None:
        return {"Error": "Could not create DB"}
    
    create_table(conn)

    user_with_crypt_pass(conn)
    R_PASS_TEST = get_user_tst(conn, "tsunapasswd")
    W_PASS_TEST = get_user_tst(conn, "wrongpass")

    delete_table(conn, "DB_TEST")

    conn.close()

    return {"Correct PASS": R_PASS_TEST, "Wrong PASS": W_PASS_TEST}