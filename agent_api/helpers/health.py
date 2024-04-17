from common.entities import DB
from common.kubernetes.readiness_probe import NotReadyException


def readiness_probe() -> None:
    if DB.obj is None:
        raise NotReadyException("Database not initialized")
