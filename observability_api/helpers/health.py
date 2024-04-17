from common.entities import DB


def readiness_probe() -> None:
    if DB.obj is None:
        raise ValueError("Database not initialized")
