from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from ..dependencies import get_db, templates
from ... import crud, schemas


router = APIRouter()


@router.get("/appium-servers", response_class=HTMLResponse)
async def appium_servers(request: Request, db: Session = Depends(get_db)):
    servers = get_appium_servers(db=db)
    return templates.TemplateResponse("appium-servers.html", {
        "request": request,
        "servers": jsonable_encoder(servers)
    })


@router.get("/api/appium_servers", response_model=list[schemas.AppiumServer])
def get_appium_servers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    servers = crud.get_appium_servers(db, skip=skip, limit=limit)
    return servers


@router.get("/api/appium_servers/{id}", response_model=schemas.AppiumServer)
def get_appium_server_by_id(id: int, db: Session = Depends(get_db)):
    server = crud.get_appium_server_by_id(db, id=id)
    if server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return server


@router.post("/api/appium_servers", response_model=schemas.AppiumServer)
def add_appium_server(appium_server_create: schemas.AppiumServerCreate, db: Session = Depends(get_db)):
    appium_server = crud.add_appium_server(db, appium_server=appium_server_create)
    return appium_server


@router.delete("/api/appium_servers/{id}", response_model=schemas.AppiumServer)
def delete_appium_by_server_id(id: int, db: Session = Depends(get_db)):
    return crud.delete_appium_server(db, appium_server_id=id)

