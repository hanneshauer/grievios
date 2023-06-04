from sqlalchemy.orm import Session

from . import models, schemas


""" Devices """


def get_devices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Device).all()


def get_device(db: Session, device_udid: str):
    return db.query(models.Device).filter(models.Device.udid == device_udid).first()


def add_device(db: Session, device: schemas.Device):
    db_device = models.Device(udid=device.udid, name=device.name, os=device.os, os_version=device.os_version)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def delete_device(db: Session, device_udid: str):
    db_device = get_device(db, device_udid=device_udid)
    if not db_device is None:
        db.delete(db_device)
        db.commit()
    return db_device


""" Appium Servers """


def get_appium_servers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AppiumServer).all()


def get_appium_server_by_id(db: Session, id: int):
    return db.query(models.AppiumServer).filter(models.AppiumServer.id == id).first()


def add_appium_server(db: Session, appium_server: schemas.AppiumServerCreate):
    db_appium_server = models.AppiumServer(url=appium_server.url, port=appium_server.port, wdaBundleId=appium_server.wdaBundleId)
    db.add(db_appium_server)
    db.commit()
    db.refresh(db_appium_server)
    return db_appium_server


def delete_appium_server(db: Session, appium_server_id: int):
    db_appium_server = get_appium_server_by_id(db, appium_server_id)
    if db_appium_server:
        db.delete(db_appium_server)
        db.commit()
    return db_appium_server


""" Explorations """


def get_explorations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Exploration).all()


def get_exploration_by_id(db: Session, id: int):
    return db.query(models.Exploration).filter(models.Exploration.id == id).first()


def add_exploration(db: Session, exploration: schemas.ExplorationCreate):
    db_exploration = models.Exploration(**exploration.dict())
    db.add(db_exploration)
    db.commit()
    db.refresh(db_exploration)
    return db_exploration


def add_explorations(db: Session, explorations: list[schemas.Exploration]):
    db_explorations: list[schemas.Exploration] = []
    for exploration in explorations:
        db_exploration = models.Exploration(**exploration.dict(), device_udid=exploration.device.udid,
                                            appium_server_id=exploration.appium_server.id)
        db.add(db_exploration)
        db.commit()
        db.refresh(db_exploration)
        db_explorations.append(db_exploration)
    return db_explorations


def delete_exploration(db: Session, exploration_id: int):
    db_exploration = get_exploration_by_id(db, id=exploration_id)
    if db_exploration:
        db.delete(db_exploration)
        db.commit()
    return db_exploration
