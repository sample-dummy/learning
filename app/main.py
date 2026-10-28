from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import create_engine, SQLModel, Field, Session, select
from typing import Annotated
from app.database import create_db_and_tables


from app.routes.students import router
from app.routes.authorize import routerAuth
from app.routes.courses import router_course

app=FastAPI()

# ⚠️⚠️If you're using Alembic, just remove this shit cause it can clash with Alembic on startup

# @app.on_event("startup")
# def on_startup():
#     create_db_and_tables()


app.include_router(router)
app.include_router(routerAuth)
app.include_router(router_course)