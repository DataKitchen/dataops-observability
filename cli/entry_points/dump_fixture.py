import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

from cli.base import DatabaseScriptBase
from common.model import walk
from common.peewee_extensions.fixtures import dump_results

LOG = logging.getLogger(__name__)
MODEL_MAP = walk()
TABLE_CHOICES = sorted([x.rsplit(".", maxsplit=1)[-1] for x in MODEL_MAP.keys()])


class DumpFixture(DatabaseScriptBase):
    """Dump fixture data from the database."""

    subcommand: str = "dump-fixture"

    @staticmethod
    def args(parser: ArgumentParser) -> None:
        parser.description = "Dump fixture data for a given table"
        parser.usage = "$ cli dump-fixture [PATH]"
        parser.add_argument("TABLE", nargs="?", choices=TABLE_CHOICES)
        parser.add_argument(
            "-o",
            "--output",
            dest="outfile",
            default=None,
            help="Output filename for fixture output",
        )

    def subcmd_entry_point(self) -> None:
        table = self.kwargs.get("TABLE")
        for name, klass in MODEL_MAP.items():
            if name.rsplit(".", maxsplit=1)[-1] == table:
                model_class = klass
                break
        else:
            LOG.error("#r<No database table matched name>: #y<%s>", table)
            sys.exit(1)

        if outfile := self.kwargs.get("outfile"):
            out_path = Path(outfile).resolve(strict=False)
            if out_path.suffix.lower() != ".toml":
                LOG.error("#r<Output file must end with a `>#y<.toml>#r<` extension.>")
                sys.exit(1)
        else:
            out_path = None

        items = model_class.select()
        total = items.count()
        if total == 0:
            LOG.error("#r<No database rows found in table>")
            sys.exit(1)

        LOG.info("Dumping #c<%s> rows...", total)
        result = dump_results(model_class.select())

        if out_path is not None:
            with out_path.open("w") as f:
                f.seek(0)
                f.truncate()
                f.write(result)
            LOG.info("#g<\u2713> Wrote #g<%s>!", out_path)
            sys.exit(0)
        else:
            sys.stdout.write(result)
            sys.stdout.flush()
            sys.stdout.write("\n")
            sys.stdout.flush()
            LOG.info("#g<\u2713> Done!")
            sys.exit(0)
