#!/bin/env python3
import sys

from ui import cli_ui
from services import services
from services.db import Database
from tools import options


def main() -> int:
        # handle options

        if options.init(sys.argv) == 1:
                print( f"Unknown options: { ', '.join(options.UNKNOWN_OPTIONS) }\n" ) if len(options.UNKNOWN_OPTIONS) > 0 else None
                cli_ui.print_help_msg()
                return 1

        if options.PRINT_HELP:
                cli_ui.print_help_msg()
                return 0

        if options.LIST_SEARCHES:
                cli_ui.print_saved_searches()
                return 0

        if options.LIST_PAGES:
                cli_ui.print_saved_pages()
                return 0



        # handle positional args

        positional_args = [a for a in sys.argv[1:] if a not in options.VALID_OPTIONS_LIST]

        if len(positional_args) == 0:
                cli_ui.print_help_msg()
                return 1

        if positional_args[0] in options.DICTIONARY_MODE_NAMES:
                page = services.fetch_wiki_page(positional_args[1:], "wiktionary")
                path = positional_args[3] if len(positional_args) >= 4 else None
                return cli_ui.print_sections(page, path) if page else 1

        elif positional_args[0] in options.TRANSLATION_MODE_NAMES:
                print("not yet supported")
                ...

        elif positional_args[0] in options.ARTICLE_MODE_NAMES:
                page = services.fetch_wiki_page(positional_args[1:], "wikipedia")
                path = positional_args[3] if len(positional_args) >= 4 else None
                return cli_ui.print_sections(page, path) if page else 1

        else:
                cli_ui.print_help_msg()
                return 1


if __name__ == "__main__":
        exit(main())
