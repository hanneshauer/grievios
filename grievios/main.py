from contextlib import asynccontextmanager
import logging
import os
import threading

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from . import crud, models
from .common import grievios_base_path
from .database import SessionLocal, engine
from .exploration import exploration_worker
from .web import routers
from .web.dependencies import get_db, templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.exploration_workers = []
    appium_servers = crud.get_appium_servers(db=SessionLocal())
    app.exploration_workers = [
        exploration_worker.ExplorationWorker(app, appium_server_id=server.id)
        for server in appium_servers
    ]
    for worker in app.exploration_workers:
        threading.Thread(target=worker.run).start()

    yield

    for worker in app.exploration_workers:
        worker.stop()


try:
    os.makedirs(grievios_base_path(), exist_ok=True)
    os.makedirs(grievios_base_path() / 'IPAs', exist_ok=True)
except OSError as e:
    logging.log(
        logging.ERROR,
        f"Failed to create GRIEviOS directories at ${grievios_base_path()}: {e}",
    )

models.Base.metadata.create_all(bind=engine)

print(os.path.dirname(__file__))

app = FastAPI(dependencies=[Depends(get_db)], lifespan=lifespan)
#app.mount("/static", StaticFiles(directory=os.path.relpath("grievios/web/static")), name="static")
app.mount("/static", StaticFiles(directory=os.path.join(os.path.abspath(os.path.dirname(__file__)), os.path.join("web", "static"))), name="static")
app.include_router(routers.devices.router)
app.include_router(routers.appium_servers.router)
app.include_router(routers.explorations.router)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    from .utils import cmdline_utils

    def check_util_availability(util: cmdline_utils.cmdline_util):
        path = None
        try:
            path = util.path()
        except cmdline_utils.cmdline_util.CmdlineUtilUnavailableException:
            pass
        return path

    utils = {
        "ideviceinstaller": {"class": cmdline_utils.Ideviceinstaller, "required": True},
        "ideviceinfo": {"class": cmdline_utils.Ideviceinfo, "required": False},
        "idevice_id": {"class": cmdline_utils.IdeviceId, "required": False},
    }

    utils_info = {
        util: {
            "name": util,
            "required": util_info["required"],
            "path": check_util_availability(util_info["class"]),
        }
        for util, util_info in utils.items()
    }

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "utilsInfo": utils_info,
            "grieviosDir": grievios_base_path(),
        },
    )


def start():
    uvicorn.run("grievios.main:app")
