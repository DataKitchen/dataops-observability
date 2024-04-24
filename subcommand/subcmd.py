# Standard
import argparse
import logging

LOG = logging.getLogger(__name__)


class SubcommandBase(type):
    """
    Subclassing this metaclass gives a simple class that can be used to manage subcommands. Classes get an attribute
    called ``parser`` which is an instance of argparse local to that class.

    Adding additional arguments is as simple as defining an ``args`` staticmethod that takes a ``parser`` object as
    it's only argument. New options can be added in this way::

        @staticmethod
        def args(parser):
            parser.usage = "A subcommand that does important cool things"
            parser.add_argument(
                "-sd",
                "--self-destruct",
                action="store_true",
                help="Determine whether or not your computer should self destruct after completing the command"
            )

    The subclassing model allows for an additive approach, meaning you can define a base class with options and then
    declare subcommands with their own options. The options of the base class will be inherited by the subclass.

    This was inspired by https://code.activestate.com/recipes/576935-argdeclare-declarative-interface-to-argparse/
    """

    def __new__(cls, class_name, class_parents, class_attr):
        args_defined = "args" in class_attr.keys()

        new_class = super().__new__(cls, class_name, class_parents, class_attr)

        root = True
        for parent in class_parents:
            if hasattr(parent, "_arg_adders"):
                root = False

        new_class._arg_adders = []

        for parent in class_parents:
            if hasattr(parent, "_arg_adders"):
                new_class._arg_adders.extend(parent._arg_adders)

        if args_defined:
            new_class._arg_adders.append(new_class.args)

        if root:
            new_class._base_parser = argparse.ArgumentParser()
            new_class._base_subparsers = new_class._base_parser.add_subparsers(dest="command")
            new_class._base_subparsers.required = True

        else:
            for parent in class_parents:
                if hasattr(parent, "_base_parser"):
                    new_class._base_parser = parent._base_parser
                    new_class._base_subparsers = parent._base_subparsers
                    break

        @classmethod
        def main(calling_class):
            args, unknown = calling_class._base_parser.parse_known_args()
            sel_run = args._run
            kwargs = vars(args)
            kwargs.pop("_main", None)
            kwargs["__unknown__"] = unknown  # Stash unknown arguments in case something wants to process them
            sel_run(**kwargs)

        new_class._main = main

        if hasattr(new_class, "subcommand"):
            new_class._parser = new_class._base_subparsers.add_parser(new_class.subcommand, conflict_handler="resolve")

            for arg_adder in new_class._arg_adders:
                arg_adder(new_class._parser)

            @classmethod
            def _run(new_class, **args):
                new_class(**args).subcmd_entry_point()

            new_class._run = _run

            new_class._parser.set_defaults(_run=new_class._run)

        return new_class
