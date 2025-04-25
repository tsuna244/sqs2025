from typing import Union

from fastapi import FastAPI, Request

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel

# imports all necessary custom modules
from modules import PokemonObj, GenerationObj


templates = Jinja2Templates(directory="app/templates")


app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
async def read_root(request: Request):
    return {"Test": "Test"}


@app.get("/Pokemon")
async def read_pokemon(request: Request):
    return PokemonObj(1).__dict__()


#@app.get("/pokesprite")
#async def read_item(request: Request):
#    return templates.TemplateResponse(
#        name="base.html",
#        request=request, 
#        context={"brand": pika.get_pokesprite_url_by_id(20, 0)}
#    )


#@app.get("/test_postgresql")
#async def create_postgres_test(request: Request):
#    conn = sql.get_postgress_conn()
#    
#    if conn is None:
#        return {"Error": "Could not create DB"}
#    
#    sql.create_table(conn)
#
#    sql.user_with_crypt_pass(conn)
#    R_PASS_TEST = sql.get_user_tst(conn, "tsunapasswd")
#    W_PASS_TEST = sql.get_user_tst(conn, "wrongpass")
#
#    sql.delete_table(conn, "DB_TEST")
#
#    conn.close()
#
#    return {"Correct PASS": R_PASS_TEST, "Wrong PASS": W_PASS_TEST}