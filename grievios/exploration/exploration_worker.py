import logging
import threading
import time


from .exploration_session_options import ExplorationSessionOptions
from .exploration_session import ExplorationSession, ServerUnavailableError, ExplorationFailedError, ExplorationStartFailedError
from .. import models
from ..common import grievios_base_path
from ..database import SessionLocal


class ExplorationWorker:
    INTERVAL: int = 10

    def __init__(self, app, appium_server_id: int):
        self.app = app
        self.appium_server_id: int = appium_server_id
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            db = SessionLocal()
            server = db.query(models.AppiumServer).filter(models.AppiumServer.id == self.appium_server_id).first()
            if not server:
                self.stop()

            exploration = db.query(models.Exploration).filter(
                models.Exploration.appium_server_id == self.appium_server_id,
                models.Exploration.status == "Created")\
                .first()
            if not exploration:
                logging.log(logging.DEBUG, f"No exploration for server {server.id} waiting, sleeping for {self.INTERVAL}s")
                db.close()
                time.sleep(self.INTERVAL)
                continue

            session_options: ExplorationSessionOptions = ExplorationSessionOptions(
                command_executor=f"{server.url}:{server.port}",  # TODO: server.basePath
                device_udid=exploration.device_udid,
                bundle_id=exploration.bundle_id,
                wda_bundle_id=server.wdaBundleId,
                strategy=exploration.strategy,
                analyzers=exploration.analyzers,
                log_directory=grievios_base_path() / "logs" / f"exploration-{str(exploration.id)}",
                bundle_installed=exploration.bundle_on_device
            )

            try:
                with ExplorationSession(self.app, session_options) as sess:
                    sess.start()
            except ServerUnavailableError:
                logging.log(logging.ERROR, "Appium server not reachable")
                time.sleep(self.INTERVAL)
                continue
            except ExplorationFailedError as e:
                logging.log(logging.ERROR, f'Exploration failed: {e}')
                exploration.status = 'Failed'
                db.commit()
                continue
            except ExplorationStartFailedError as e:
                logging.log(logging.ERROR, f'Exploration failed to start: {e.cause}')
                exploration.status = 'Failed'
                db.commit()
                continue

            except Exception as e:
                logging.log(logging.ERROR, f'Exploration failed unexpectedly: {e}')
                exploration.status = 'Failed'
                db.commit()
                continue

            exploration.status = 'Finished'
            db.commit()

            db.close()
