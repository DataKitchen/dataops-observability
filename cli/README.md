# Observability CLI

A simple framework for adding useful administrative/developer helper scripts and tooling. It provides an entry-point
named ``cli`` to which new and exciting and helpful tools can be added.

It's designed to be very easy to extend; all the tricky work is done for you. You provide a subclass, add the module
to a file, and everything is nicely encapsulated into a single command line interface.

The intent is to make it vanishingly simple for a developer to add new subcommands while keeping the interface
consistent with tools all scoped to a single module.


## Usage

All entry-points are available as subcommands of ``cli`` once installed. All subcommands automatically get the
following arguments by default:

- ``--environment`` Set to "dev", "local", etc.. to force running with a specific environment configuration
- ``-l`` | ``--log-level`` Choose logging output level: DEBUG, INFO, etc...
- ``-L`` | ``--logfile`` Additionally write the output to a log file (ANSI color codes are stripped)
- ``-V`` | ``--version`` Outputs the currently installed application version and exits


## Adding a new script

- Place new scripts in ``cli/entry_points/`` folder
- Inherit from ``cli.base.ScriptBase``
- Give the subcommand a name and add any arguments
- Create a ``subcmd_entry_point`` method to do the main heavy lifting
- Add path to new script in ``cli/__init__.py`` in the ``modules`` tuple
- Emphasize command-line output by adding colors!

Example script for ``cli/entry_points/cool_script.py``:

```python
import  logging
from argparse import ArgumentParser

from cli.base import SubcommandBase

LOG = logging.getLogger(__name__)


class CoolScript(SubcommandBase):

    subcommand: str = "coolistic"

    @staticmethod
    def args(parser: ArgumentParser) -> None:
        parser.description = "Write a name in a cool cyan color."
        parser.usage = "$ cli coolistic [NAME]"
        parser.add_argument("NAME", nargs="?")

    def subcmd_entry_point(self) -> None:
        name = self.kwargs.get("NAME")
        # NOTE: surrounding text with #c< whatevz > is what adds the cool cyan color. You can also do b (blue),
        # r (red), g (green), y (yellow), w (white)
        LOG.info("Cool name bruh: #c<%s>", name)
```


Adding to the ``__init__`` file:


```python
# ... some file stuff ...
modules: Tuple[str, ...] = (
    "cli.entry_points.service_account_key",
    "cli.entry_points.cool_script",
)
```

And voila! You'll have a new usable subcommand.
