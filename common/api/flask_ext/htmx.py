__all__ = ["HTMX"]

import logging

from flask import g, request

from .base_extension import BaseExtension

LOG = logging.getLogger(__name__)


class HTMX(BaseExtension):
    @staticmethod
    def process_htmx_headers() -> None:
        get_header = request.headers.get  # Stash to avoid repeated attribute lookups

        # Boolean values
        g.is_htmx = get_header("HX-Request") == "true"
        g.hx_boosted = get_header("HX-Boosted") == "true"
        g.hx_history_restore_request = get_header("HX-History-Restore-Request") == "true"

        # Determine if async in general
        g.is_async = g.is_htmx and not g.hx_boosted

        # Text values
        g.hx_current_url = get_header("HX-Current-URL") or ""
        g.hx_prompt = get_header("HX-Prompt") or ""
        g.hx_target = get_header("HX-Target") or ""
        g.hx_trigger = get_header("HX-Trigger") or ""
        g.hx_trigger_name = get_header("HX-Trigger-Name") or ""

    def init_app(self) -> None:
        if self.app is not None:
            self.add_before_request_func(HTMX.process_htmx_headers)
