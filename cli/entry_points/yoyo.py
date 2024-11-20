import logging
import sys
from argparse import ArgumentParser

from yoyo import get_backend, read_migrations
from yoyo.scripts.main import configure_logging

from conf import settings
from cli.base import DatabaseScriptBase

LOG = logging.getLogger(__name__)


class OperationAborted(Exception):
    pass


class Migrate(DatabaseScriptBase):
    """
    Updates the Database Schema.

    We use the DatabaseScriptBase to take advantage of the high-level validation of the database settings, but yoyo
    connects to the database independently.
    """

    subcommand: str = "migrate"

    @staticmethod
    def args(parser: ArgumentParser) -> None:
        parser.description = "Yoyo Migration Tool Wrapper"
        parser.usage = "$ cli migrate"

    def subcmd_entry_point(self) -> None:
        try:
            self.apply_migrations()
        except OperationAborted as e:
            LOG.info("Operation #y<ABORTED>: %s", e)
            sys.exit(1)
        except Exception as e:
            LOG.error("Operation #r<FAILED>: %s", e)
            sys.exit(2)
        else:
            LOG.info("Operation #g<SUCCEEDED>")

    def _get_yoyo_url(self) -> str:
        db_settings = settings.DATABASE
        return (
            f"mysql://{db_settings['user']}:{db_settings['passwd']}@"
            f"{db_settings['host']}:{db_settings['port']}/{db_settings['name']}"
        )

    def apply_migrations(self, force: bool = False) -> None:
        # 3 is the most verbose mode supported. That way, we just let our logging config cap it if needed.
        configure_logging(3)
        backend = get_backend(self._get_yoyo_url())
        migrations = read_migrations(settings.MIGRATIONS_SRC_PATH)

        with backend.lock():
            to_be_applied = backend.to_apply(migrations)

            applied = []
            try:
                LOG.info("Applying %d migrations...", len(to_be_applied))
                for migration in to_be_applied:
                    try:
                        backend.apply_one(migration, force=force)
                    except Exception as e:
                        LOG.error("Migration '%s' FAILED: %s", migration.id, e)
                        raise
                    else:
                        LOG.info("Migration '%s' SUCCEEDED", migration.id)
                        applied.append(migration)
            except Exception as e:
                for migration in reversed(applied):
                    LOG.info("  '-- Rolling back '%s'", migration.id)
                    try:
                        backend.rollback_one(migration, force=True)
                    except Exception as rollback_exp:
                        LOG.exception("Error rolling back migration '%s': %s", migration.id, rollback_exp)

                raise OperationAborted("Migration failed. The new migrations have been rolled back") from e

            backend.run_post_apply(migrations, force=force)
