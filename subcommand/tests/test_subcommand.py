import pytest

from subcommand import SubcommandBase


class TopLevel(metaclass=SubcommandBase):
    subcommand = "top-level-cmd"

    @staticmethod
    def args(parser):
        parser.add_argument("positionalarg")
        parser.add_argument("-k", "--keyarg")
        parser.add_argument("-kk", "--keyarg2")


class Level2(TopLevel):
    subcommand = "level2"

    @staticmethod
    def args(parser):
        parser.add_argument("--fizz")


class Level3(Level2):
    subcommand = "level3"

    @staticmethod
    def args(parser):
        parser.add_argument("--buzz")


class Level3Alt(Level2):
    subcommand = "level3alt"

    @staticmethod
    def args(parser):
        parser.add_argument("--neil")


@pytest.mark.unit
def test_help():
    """Calling help from any subcommand classes parser should exit immeditately."""
    with pytest.raises(SystemExit):
        TopLevel._base_parser.parse_args(["-h"])
    with pytest.raises(SystemExit):
        TopLevel._base_parser.parse_args(["--help"])
    with pytest.raises(SystemExit):
        TopLevel._base_parser.parse_args(["top-level-cmd", "--help"])
    with pytest.raises(SystemExit):
        Level2._base_parser.parse_args(["-h"])
    with pytest.raises(SystemExit):
        Level2._base_parser.parse_args(["--help"])
    with pytest.raises(SystemExit):
        Level2._base_parser.parse_args(["level2", "--help"])
    with pytest.raises(SystemExit):
        Level3._base_parser.parse_args(["-h"])
    with pytest.raises(SystemExit):
        Level3._base_parser.parse_args(["--help"])
    with pytest.raises(SystemExit):
        Level3._base_parser.parse_args(["level3", "--help"])


@pytest.mark.unit
def test_parse():
    args = TopLevel._base_parser.parse_args(["top-level-cmd", "cool-arg-1", "-k", "mykey", "-kk", "mykey2"])

    expected_vars = {"command": "top-level-cmd", "positionalarg": "cool-arg-1", "keyarg": "mykey", "keyarg2": "mykey2"}
    vargs = vars(args)

    # Ensure all expected keys exist
    for key in expected_vars.keys():
        assert key in vargs, f"Parsed arguments are missing key {key}"

    # Ensure parsed values match
    for key, value in expected_vars.items():
        assert vargs[key] == value, f"{key} got parsed value {vargs[key]} - expected: {value}"


@pytest.mark.unit
def test_level2_inherit():
    args = Level2._base_parser.parse_args(["level2", "cool-arg-2", "-k", "mykey", "-kk", "mykey2", "--fizz", "cola"])

    expected_vars = {
        "command": "level2",
        "positionalarg": "cool-arg-2",
        "keyarg": "mykey",
        "keyarg2": "mykey2",
        "fizz": "cola",
    }
    vargs = vars(args)

    # Ensure all expected keys exist
    for key in expected_vars.keys():
        assert key in vargs, f"Parsed arguments are missing key {key}"

    # Ensure parsed values match
    for key, value in expected_vars.items():
        assert vargs[key] == value, f"{key} got parsed value {vargs[key]} - expected: {value}"


@pytest.mark.unit
def test_level3_inherit():
    args = Level3._base_parser.parse_args(
        ["level3", "cool-arg-3", "-k", "mykey", "-kk", "mykey2", "--fizz", "cola", "--buzz", "lightyear"]
    )

    expected_vars = {
        "command": "level3",
        "positionalarg": "cool-arg-3",
        "keyarg": "mykey",
        "keyarg2": "mykey2",
        "fizz": "cola",
        "buzz": "lightyear",
    }
    vargs = vars(args)

    # Ensure all expected keys exist
    for key in expected_vars.keys():
        assert key in vargs, f"Parsed arguments are missing key {key}"

    # Ensure parsed values match
    for key, value in expected_vars.items():
        assert vargs[key] == value, f"{key} got parsed value {vargs[key]} - expected: {value}"


@pytest.mark.unit
def test_sibbling_interference():
    """Sibbling parsers should not share arguments."""
    sibling1_args = Level3._base_parser.parse_args(
        ["level3", "cool-arg-3", "-k", "mykey", "-kk", "mykey2", "--fizz", "cola", "--buzz", "lightyear"]
    )
    sibbling1_vargs = vars(sibling1_args)

    sibling2_args = Level3Alt._base_parser.parse_args(
        ["level3alt", "cool-arg-3", "-k", "mykey", "-kk", "mykey2", "--fizz", "cola", "--neil", "armstrong"]
    )
    sibbling2_vargs = vars(sibling2_args)

    assert "neil" not in sibbling1_vargs, "Argument `neil` should not be shared with sibbling parsers"
    assert "buzz" not in sibbling2_vargs, "Argument `buzz` should not be shared with sibbling parsers"
