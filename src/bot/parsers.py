import argparse
from functools import lru_cache, partial
from typing import List
from dataclasses import dataclass

from src.models import CommandsForGenerate, CommandsForPolling


class ParseError(Exception):
    def __init__(self, *args, help: str = "", **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.help = help


class CustomArgumentParser(argparse.ArgumentParser):
    def format_help(self) -> str:
        _help = super().format_help()

        subparsers_actions = [
            action
            for action in self._actions
            if isinstance(action, argparse._SubParsersAction)
        ]

        for subparsers_action in subparsers_actions:
            for choice, subparser in subparsers_action.choices.items():
                _help += f"\nHelp for subcommand: {choice}\n{subparser.format_help()}"

        return _help

    def parse_known_args(
        self, args: List = None, namespace: argparse.Namespace = None
    ) -> argparse.Namespace:
        try:
            namespace, args = super().parse_known_args(args=args, namespace=namespace)

            if args:
                raise ParseError

            return namespace, args

        except (SystemExit, argparse.ArgumentError, ParseError) as exc:
            # crutch https://github.com/python/cpython/issues/90598
            return argparse.Namespace(err=exc, help=self.format_help()), args

    def parse(self, args: List) -> argparse.Namespace:
        namespace, _ = self.parse_known_args(args=args)

        if self._parse_error_exists(namespace):
            raise ParseError(help=namespace.help)

        return namespace

    @staticmethod
    def _parse_error_exists(namespace: argparse.Namespace) -> bool:
        return getattr(namespace, "err", None) and isinstance(
            namespace.err, BaseException
        )


@lru_cache()
def get_polling_parser() -> CustomArgumentParser:
    parser = CustomArgumentParser(
        description="Process some integers.", exit_on_error=False, usage="/polling"
    )

    subparser = parser.add_subparsers(required=False)

    _setup_start_parser(subparser.add_parser(CommandsForPolling.START.value))
    _setup_settings_parser(subparser.add_parser(CommandsForPolling.SETTINGS.value))
    _setup_stop_parser(subparser.add_parser(CommandsForPolling.STOP.value))

    return parser


@lru_cache()
def get_generate_parser() -> CustomArgumentParser:
    parser = CustomArgumentParser(
        description="Process some integers.", exit_on_error=False, usage="/generate"
    )

    parser.add_argument(
        "--generate-command",
        type=CommandsForGenerate,
        default=CommandsForGenerate.ALL,
        choices=[v.value for v in CommandsForGenerate.__members__.values()],
        help="lalalala",
    )

    return parser


def _setup_start_parser(parser: CustomArgumentParser) -> None:
    parser.add_argument(
        "-c",
        dest="command",
        action="store_const",
        const=CommandsForPolling.START,
        default=CommandsForPolling.START,
    )
    parser.add_argument(
        "--when", "-w", default="5m", help="When to start congratulating"
    )


def _setup_settings_parser(parser: CustomArgumentParser) -> None:
    parser.add_argument(
        "-c",
        dest="command",
        action="store_const",
        const=CommandsForPolling.START,
        default=CommandsForPolling.START,
    )
    parser.add_argument(
        "--names",
        "-n",
        nargs="+",
        required=True,
        help="Names of girls to be congratulated",
    )
    parser.add_argument(
        "--delay", "-d", default="5m", help="Delay between congratulations (default 5m)"
    )


def _setup_stop_parser(parser: CustomArgumentParser) -> None:
    parser.add_argument(
        "-c",
        dest="command",
        action="store_const",
        const=CommandsForPolling.START,
        default=CommandsForPolling.START,
    )
    parser.add_argument(
        "--when", "-w", default="5m", help="When to stop congratulating"
    )
