import logging

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from ..dependencies import get_db, templates
from ... import analyzers, strategies
from ... import crud, schemas, common
from ...utils import ipa

router = APIRouter()


@router.get("/explorations", response_class=HTMLResponse)
async def explorations(request: Request, db: Session = Depends(get_db)):
    db_explorations = crud.get_explorations(db=db)
    db_devices = crud.get_devices(db=db)
    db_servers = crud.get_appium_servers(db=db)
    local_ipas = ipa.scan_directory(common.grievios_base_path() / 'IPAs')
    return templates.TemplateResponse("explorations.html", {
        "request": request,
        "explorations": jsonable_encoder(db_explorations),
        "devices": jsonable_encoder(db_devices),
        "servers": jsonable_encoder(db_servers),
        "strategies": strategies.ios.availableStrategies(),
        "analyzers": analyzers.ios.availableAnalyzers(),
        "localIpas": jsonable_encoder(local_ipas)
    })


@router.get("/api/explorations", response_model=list[schemas.Exploration])
def get_explorations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_explorations = crud.get_explorations(db, skip=skip, limit=limit)
    return db_explorations


@router.post("/api/explorations", response_model=list[schemas.Exploration])
def add_explorations(explorationInput: schemas.ExplorationInput, db: Session = Depends(get_db)):
    try:
        device = crud.get_device(db, device_udid=explorationInput.device)
    except:
        raise HTTPException(status_code=404, detail=f"Device {explorationInput.device} not found")
    try:
        server = crud.get_appium_server_by_id(db, id=explorationInput.appiumServer)
    except:
        raise HTTPException(status_code=404, detail="Server not found")
    db_explorations: list[schemas.Exploration] = []
    for strategy in explorationInput.strategies:
        for localApp in explorationInput.localApps:
            try:
                newExploration = schemas.ExplorationCreate(
                    device_udid=device.udid,
                    appium_server_id=server.id,
                    status="Created",
                    bundle_id=localApp,
                    bundle_on_device=False,
                    strategy=strategy,
                    analyzers=explorationInput.analyzers
                )
                db_exploration = crud.add_exploration(db, newExploration)
                db_explorations.append(db_exploration)
            except Exception as e:
                logging.log(logging.ERROR, f"Error adding new exploration: {e}")
                continue

    return db_explorations


@router.put("/api/explorations/{exploration_id}/status/reset", response_model=schemas.Exploration)
def update_exploration(exploration_id: int, db: Session = Depends(get_db)):
    try:
        exploration: schemas.Exploration = crud.get_exploration_by_id(db, exploration_id)
    except:
        raise HTTPException(status_code=404, detail=f"Exploration {exploration_id} not found")
    exploration.status = 'Created'
    db.commit()
    return exploration


@router.delete("/api/explorations/{exploration_id}")
def delete_exploration_by_id(exploration_id: int, db: Session = Depends(get_db)):
    return crud.delete_exploration(db, exploration_id=exploration_id)
