#!/bin/env python3

import sys 

from ui import cli_ui
from services import services
from services.db import Database
from tools import options


def main() -> int:
        # handle options 

        if options.init(sys.argv) == 1:
                print( f"Unknown options: { ', '.join(options.unknown_options) }\n" ) if len(options.unknown_options) > 0 else None
                cli_ui.print_help_msg()
                return 1

        if options.print_help:
                cli_ui.print_help_msg()
                return 0

        if options.list_searches:
                cli_ui.print_saved_searches()
                return 0
        
        if options.list_pages:
                cli_ui.print_saved_pages()
                return 0



        # handle positional args

        positional_args = [a for a in sys.argv[1:] if a not in options.valid_options_list] 

        if len(positional_args) == 0:
                cli_ui.print_help_msg()
                return 1

        translate_mode_names = ["t", "tr", "translate"]
        dict_mode_names = ["d", "dict", "dictionary"]
        wiki_mode_names = ["w", "wiki", "wikipedia"]

        if positional_args[0] in dict_mode_names:
                page = services.wiki_page(positional_args[1:], "wiktionary")
                path = positional_args[3] if len(positional_args) >= 4 else None
                return cli_ui.print_sections(page, path) if page else 1

        elif positional_args[0] in translate_mode_names:
                ...

        elif positional_args[0] in wiki_mode_names:
                page = services.wiki_page(positional_args[1:], "wikipedia")
                path = positional_args[3] if len(positional_args) >= 4 else None
                return cli_ui.print_sections(page, path) if page else 1

        else:
                cli_ui.print_help_msg()
                return 1


if __name__ == "__main__":
        exit(main())
