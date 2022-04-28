import pytest
import argparse

from src.bot.parsers import get_generate_parser, get_polling_parser, ParseError
from src.models import CommandsForGenerate, CommandsForPolling


def test_generator_parser_simple() -> None:
    parser = get_generate_parser()
    args: GenerateArgs = parser.parse([])

    assert args.generate_command == CommandsForGenerate.ALL


def test_generator_parser_with_args() -> None:
    parser = get_generate_parser()
    args = parser.parse(["--generate-command", "text"])

    assert args.generate_command == CommandsForGenerate.TEXT


def test_polling_parser_for_polling_with_empty_args() -> None:
    parser = get_polling_parser()

    with pytest.raises(ParseError) as err_info:
        parser.parse(["settings"])


def test_polling_parser_for_polling_settings_simple() -> None:
    parser = get_polling_parser()

    args = parser.parse("settings --names testik_1 testik_2".split())

    assert args.names == ["testik_1", "testik_2"]
    assert args.delay == "5m"


def test_polling_parser_for_polling_start_simple() -> None:
    parser = get_polling_parser()

    args = parser.parse(["start"])

    assert args.when == "5m"


def test_polling_parser_for_polling_stop_simple() -> None:
    parser = get_polling_parser()

    args = parser.parse(["stop"])

    assert args.when == "5m"


def test_polling_parser_for_polling_wrong_command() -> None:
    parser = get_polling_parser()

    with pytest.raises(ParseError) as err_info:
        parser.parse(["wrong"])
