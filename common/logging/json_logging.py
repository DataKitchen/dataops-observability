__all__ = ["JsonFormatter"]

import logging
from datetime import datetime, UTC
from json import dumps

from common.json_encoder import JsonExtendedEncoder

UTC = UTC


class JsonFormatter(logging.Formatter):
    """A log formatter that outputs JSON; useful for logging to ELK or other logging services."""

    EXCLUDE = ("msg", "args", "exc_info", "stack_info")

    def format(self, record: logging.LogRecord) -> str:
        record_dict = {k: v for k, v in record.__dict__.items() if k not in self.EXCLUDE}
        utc_dt_obj = datetime.utcfromtimestamp(record.created).replace(tzinfo=UTC)
        record_dict["timestamp"] = utc_dt_obj.isoformat()
        record_dict["message"] = record.getMessage()
        record_dict["traceback"] = self.formatException(record.exc_info) if record.exc_info else None
        record_dict["stackinfo"] = self.formatStack(record.stack_info) if record.stack_info else None
        return dumps(record_dict, sort_keys=True, cls=JsonExtendedEncoder)
