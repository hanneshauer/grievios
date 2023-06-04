import pathlib

from pydantic import BaseModel, validator

from . import models


class DeviceBase(BaseModel):
    udid: str
    name: str = ""
    os: str = ""
    os_version: str = ""


class DeviceCreate(DeviceBase):
    pass


class Device(DeviceBase):
    name: str
    os: str
    os_version: str

    class Config:
        orm_mode = True
        orm_model = models.Device


class DeviceConnected(DeviceBase):
    pass


class AppiumServerBase(BaseModel):
    url: str
    port: int
    wdaBundleId: str


class AppiumServerCreate(AppiumServerBase):
    pass


class AppiumServer(AppiumServerBase):
    id: int

    class Config:
        orm_mode = True
        orm_model = models.AppiumServer


class ExplorationBase(BaseModel):
    #device: Device
    #appium_server: AppiumServer
    status: str
    bundle_id: str
    bundle_on_device: bool
    strategy: str
    analyzers: list[str] = []


class ExplorationCreate(ExplorationBase):
    device_udid: str
    appium_server_id: int
    pass


class Exploration(ExplorationBase):
    id: int
    device: Device
    appium_server: AppiumServer

    class Config:
        orm_mode = True
        orm_model = models.Exploration


class ExplorationInput(BaseModel):
    appiumServer: int
    device: str
    strategies: list[str]
    analyzers: list[str]
    installedApps: list[str]
    localApps: list[str]


class IPA(BaseModel):
    bundle_id: str
    minimum_os_version: str = None
    supported_platforms: list[str] = None
    bundle_name: str = None
    display_name: str = None
    bundle_version: str = None
    app_icon_path: pathlib.Path = None
    path: pathlib.Path = None
