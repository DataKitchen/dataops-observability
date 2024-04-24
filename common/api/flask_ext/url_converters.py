from werkzeug.routing import UUIDConverter

from .base_extension import BaseExtension


class UUIDDBConverter(UUIDConverter):
    """
    This converter accepts UUIDs, with or without dashes. It's meant to
    allow us to use the values peewee stores in the DB, raw. the UUID
    library is smart enough to do this; the flask default covnerter just has an
    incomplete regex value.
    """

    # Support either a normal "8-4-4-4-12" string, or a 32 character string.
    regex = r"([A-Fa-f0-9]{8}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{12})|([A-Fa-f0-9]{32})"


class URLConverters(BaseExtension):
    """
    WARNING: This needs to go before the endpoints are built (build_v1_routes) or the rules will not
             be added correctly.
    """

    def init_app(self) -> None:
        # Replace default UUID Converter with the improved version.
        self.app.url_map.converters["uuid"] = UUIDDBConverter
