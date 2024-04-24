import logging
import os
import sys
from pathlib import Path
from shutil import which
from subprocess import run
from typing import NoReturn

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler(sys.stdout))


OBSERVABILITY_API_DOCUMENT_SETTINGS = {
    "api_name": "observability@v1",
    "title": "DataKitchen Observability Observability API",
    "output_file": "observability.html",
}

EVENTS_API_DOCUMENT_SETTINGS_V1 = {
    "api_name": "event@v1",
    "title": "Event Ingestion API for DataKitchen’s DataOps Observability",
    "output_file": "events.html",
}


EVENTS_API_DOCUMENT_SETTINGS_V2 = {
    "api_name": "event@v2",
    "title": "Event Ingestion API for DataKitchen’s DataOps Observability",
    "output_file": "events_v2.html",
}


def check_requirements(*document_settings: dict) -> None:
    if which("npx") is None:
        LOG.error("Missing npx. Check installation.")
        raise SystemExit(1)

    if which("find") is None:
        LOG.error("Missing find. Check installation.")
        raise SystemExit(1)

    if not os.path.exists("deploy/pages/index.html"):
        LOG.error("Missing deploy/pages/index.html. Check cwd?")
        raise SystemExit(1)


def build_html_file(document_settings: dict) -> Path:
    LOG.info("building %s...", document_settings["output_file"])

    result = run(
        (
            f"npx @redocly/cli@1.0.0-beta.112 build-docs -o '{document_settings['output_file']}' '{document_settings['api_name']}' "
            f"--title '{document_settings['title']}' "
            "--templateOptions.sortTagsAlphabetically=true "
            "--templateOptions.sortOperationsAlphabetically=true"
        ),
        capture_output=True,
        shell=True,
    )
    if result.returncode != 0:
        LOG.error("redoc-cli call failed. Exit-code=%d", result.returncode)
        LOG.error("standard-out: %s", result.stdout.decode("utf-8"))
        LOG.error("standard-err: %s", result.stderr.decode("utf-8"))
        raise SystemExit(1)

    return Path(document_settings["output_file"])


def get_public_dir_contents() -> str:
    return run(["find", "public", "-type", "f"], check=True, capture_output=True).stdout.decode("utf-8")


def main() -> NoReturn:
    check_requirements(EVENTS_API_DOCUMENT_SETTINGS_V1, OBSERVABILITY_API_DOCUMENT_SETTINGS)

    files = map(
        build_html_file,
        (EVENTS_API_DOCUMENT_SETTINGS_V1, EVENTS_API_DOCUMENT_SETTINGS_V2, OBSERVABILITY_API_DOCUMENT_SETTINGS),
    )
    LOG.info("Built files:\n%s", "\n".join(file.name for file in files))

    sys.exit(0)


if __name__ == "__main__":
    main()
