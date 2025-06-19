import logging
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader
from peewee import Field, ForeignKeyField, ManyToManyField, Model

from cli.base import ScriptBase
from common.model import walk

LOG = logging.getLogger(__name__)
TEMPLATE_DIR = Path(__file__).resolve().parent.parent.joinpath("graph_templates")
JINJA_ENV = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)


class GraphSchema(ScriptBase):
    """Generate a schema graph from the peewee model schema."""

    subcommand: str = "graph-schema"

    @staticmethod
    def args(parser: ArgumentParser) -> None:
        parser.description = "Generate a schema graph in graphviz format."
        parser.usage = "$ cli graph-schema"
        parser.add_argument(
            "-o",
            "--output",
            dest="outfile",
            default=None,
            help="Output filename for graph output",
        )

    def subcmd_entry_point(self) -> None:
        try:
            model_map = walk()
        except Exception:
            LOG.error("#r<\u2717> Unable to walk peewee models")
            sys.exit(1)

        if outfile := self.kwargs.get("outfile"):
            out_path = Path(outfile).resolve(strict=False)
            if out_path.suffix.lower() != ".dot":
                LOG.warning(f"renaming {out_path} -> {out_path.with_suffix('.dot')}")
                out_path = out_path.with_suffix(".dot")
        else:
            out_path = None

        # Create a reversed map so we can lookup the name from the model class
        rev_map = {v: k for k, v in model_map.items()}

        # Render the static header & start a list of graph pieces to combine later
        head = JINJA_ENV.get_template("head.html")
        dot_parts = [head.render({})]

        # Initial context/config
        model_context: list[dict[str, Any]] = []

        LOG.info("#m<Graphing models...>")
        for name, model in model_map.items():
            LOG.debug("Graphing #c<%s>", name)

            # Aggregate template context
            fields = []
            relations = []

            # Append information if its a relationship
            for rel_name, field in model._meta.fields.items():
                # Calculate relationship links
                def add_relation(
                    field: Field,
                    label: str,
                    target_model: Model,
                    arrowhead: str = "",
                    direction: str = "",
                    line_style: str = "",
                ) -> None:
                    arrow_parts = []
                    if arrowhead:
                        arrow_parts.append(f"arrowhead={arrowhead}")
                    if direction:
                        arrow_parts.append(f"dir={direction}")
                    if line_style:
                        arrow_parts.append(f"style={line_style}")

                    if arrow_parts:
                        extras = f"[{', '.join(arrow_parts)}]"
                    else:
                        extras = ""

                    try:
                        target_name = rev_map[target_model]
                    except KeyError:
                        # A link to a module that doesn't exist, just list it's
                        # name.
                        target_name = target_model.__name__
                    _rel = {
                        "target_app": "",
                        "target": target_name.replace(".", "_"),
                        "type": type(field).__name__,
                        "name": label,
                        "label": label,
                        "arrows": extras,
                        "needs_node": True,
                    }
                    if _rel not in relations:
                        relations.append(_rel)

                # Track references
                if isinstance(field, ForeignKeyField):
                    add_relation(field, rel_name, field.rel_model, arrowhead="normal", direction="forward")
                elif isinstance(field, ManyToManyField):
                    add_relation(
                        field, rel_name, field.rel_model, arrowhead="normal", line_style="dotted", direction="forward"
                    )

                fields.append(
                    {
                        "name": rel_name,
                        "label": rel_name,
                        "type": type(field).__name__,
                        "blank": False,
                        "abstract": False,
                    }
                )

            model_context.append(
                {
                    "name": name.replace(".", "_"),
                    "label": name,
                    "fields": fields,
                    "relations": relations,
                }
            )

        graph = {
            "name": '"Observability Schema"',
            "app_name": "common.entities",
            "cluster_app_name": "cluster_common_entities",
            "disable_fields": False,
            "use_subgraph": False,
            "models": model_context,
        }

        nodes = []
        nodes.extend([e["name"] for e in model_context])
        graph["models"] = model_context

        # don't draw duplication nodes because of relations
        for model in model_context:
            for relation in model["relations"]:
                if relation["target"] in nodes:
                    relation["needs_node"] = False

        # Render all our FK & M2M relationships
        rel = JINJA_ENV.get_template("rel.html")
        dot_parts.append(rel.render(graph))

        # Render the main body template
        body = JINJA_ENV.get_template("body.html")
        dot_parts.append(body.render(graph))

        # Render the closing tags and whatnot
        tail = JINJA_ENV.get_template("tail.html")
        dot_parts.append(tail.render({}))

        LOG.debug("Combining graph parts into final document...")
        dot = "\n".join(dot_parts)

        if out_path is not None:
            with out_path.open("w") as f:
                f.seek(0)
                f.truncate()
                f.write(dot)
            LOG.info("#g<\u2713> Wrote #g<%s>!", out_path)
            LOG.info(
                "You can convert the output file to an image using the `dot` command:\n#c<$ dot -Tpng %s -o %s.png>\n\n...or view it with xdot or a compatible viewer:\n#c<$ xdot %s>",
                out_path.name,
                out_path.stem,
                out_path.name,
            )
            sys.exit(0)
        else:
            sys.stdout.write(dot)
            sys.stdout.flush()
            sys.stdout.write("\n")
            sys.stdout.flush()
            LOG.info("#g<\u2713> Done!")
            sys.exit(0)
