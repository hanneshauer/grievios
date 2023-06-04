from sqlalchemy import Boolean, Column, Integer, Text, PickleType, ForeignKey
from sqlalchemy.orm import relationship, mapped_column

from .database import Base


class Device(Base):
    __tablename__ = "devices"

    udid = Column(Text, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    os = Column(Text, nullable=False)
    os_version = Column(Text, nullable=False)


class AppiumServer(Base):
    __tablename__ = "appium_servers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text, nullable=False)
    port = Column(Integer, nullable=False)
    wdaBundleId = Column(Text)


class Exploration(Base):
    __tablename__ = "explorations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_udid = mapped_column(ForeignKey("devices.udid"))
    appium_server_id = mapped_column(ForeignKey("appium_servers.id"))
    status = Column(Text, nullable=False)
    bundle_id = Column(Text, nullable=False)
    bundle_on_device = Column(Boolean, nullable=False)
    strategy = Column(Text, nullable=False)
    analyzers = Column(PickleType, nullable=False)

    device = relationship("Device", lazy="selectin")
    appium_server = relationship("AppiumServer", lazy="selectin")
