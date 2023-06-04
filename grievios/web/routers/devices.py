from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from ..dependencies import get_db, templates
from ... import crud, schemas
from ...utils.cmdline_utils import IdeviceId, Ideviceinfo
from ...utils.cmdline_utils.cmdline_util import CmdlineUtilUnavailableException

router = APIRouter()


@router.get("/devices", response_class=HTMLResponse)
async def devices(request: Request, db: Session = Depends(get_db)):
    devices = get_devices(db=db)
    return templates.TemplateResponse("devices.html", {"request": request, "devices": jsonable_encoder(devices)})


@router.get("/api/devices", response_model=list[schemas.Device])
def get_devices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    devices = crud.get_devices(db, skip=skip, limit=limit)
    return devices


@router.get("/api/devices/connected", response_model=list[schemas.DeviceConnected])
def get_connected_devices():
    def get_ideviceinfos(device: schemas.DeviceConnected) -> schemas.DeviceConnected:
        infos = Ideviceinfo.run(device, ["DeviceName", "ProductName", "ProductVersion"])
        device.name = infos["DeviceName"]
        device.os = infos["ProductName"]
        device.os_version = infos["ProductVersion"]
        return device

    connected_devices: list[schemas.DeviceConnected] = []
    try:
        connected_devices = IdeviceId.run()
        connected_devices = [get_ideviceinfos(d) for d in connected_devices]
    except CmdlineUtilUnavailableException:
        pass
    return connected_devices


@router.get("/api/devices/{device_udid}", response_model=schemas.Device)
def get_device(device_udid: str, db: Session = Depends(get_db)):
    device = crud.get_device(db, device_udid=device_udid)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.post("/api/devices", response_model=schemas.Device)
def add_device(device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    db_device = crud.add_device(db, device=device)
    return db_device


@router.delete("/api/devices/{device_udid}")
def delete_device(device_udid: str, db: Session = Depends(get_db)):
    deleted_device = crud.delete_device(db, device_udid=device_udid)
    if deleted_device is None:
        raise HTTPException(status_code=404, detail=f"Device {device_udid} not found")
