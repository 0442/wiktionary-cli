#!/bin/env python3

import sys 
from time import sleep
import sys
import ui.cli_ui as cli_ui
import services.services as services
from services.db import Database

def main() -> int:
        #TODO add more options, e.g. one for including quotations in dictionary output
        # option for resolving redirects when getting page from wiki



        options = [opt for opt in sys.argv if opt.startswith("-")]
        positional_args = [arg for arg in sys.argv[1:] if arg not in options] 



        # handle options

        valid_options = ["-r", "--raw", "-h", "--help", "-ls", "--list-searches", "-lp", "--list-pages", "-f", "--force-web", "-s", "--search"]
        invalid_opts  = [opt for opt in options if opt not in valid_options]
        if invalid_opts:
                print( f"Unknown options: { ', '.join(invalid_opts) }\n" ) if len(invalid_opts) > 0 else None
                cli_ui.print_help_msg()
                return 1

        if "-h" in options or "--help" in options:
                cli_ui.print_help_msg()
                return 0

        do_formatting = False if "-r" in options or "--raw" in options else True
        force_web = True if "-f" in options or "--force-web" in options else False
        do_search = True if "-s" in options or "--search" in options else False

        if "-ls" in options or "--list-searches" in options:
                # TODO: option to group output by search word and count similar ones
                return cli_ui.print_saved_searches(do_formatting=do_formatting)

        if "-lp" in options or "--list-pages" in options:
                return cli_ui.print_saved_pages(do_formatting=do_formatting)
        


        # handle positional args

        if len(positional_args) == 0:
                cli_ui.print_help_msg()
                return 1

        translate_mode_names = ["t", "tr", "translate"]
        dict_mode_names = ["d", "dict", "dictionary"]
        wiki_mode_names = ["w", "wiki", "wikipedia"]

        if positional_args[0] in dict_mode_names:
                page = services.wiki_page(positional_args[1:], "wiktionary", force_web=force_web, do_search=do_search)
                path = positional_args[3] if len(positional_args) >= 4 else None
                return cli_ui.print_sections(page, path, do_formatting=do_formatting) if page else 1

        elif positional_args[0] in translate_mode_names:
                ...

        elif positional_args[0] in wiki_mode_names:
                page = services.wiki_page(positional_args[1:], "wikipedia", force_web=force_web, do_search=do_search)
                path = positional_args[3] if len(positional_args) >= 4 else None
                return cli_ui.print_sections(page, path, do_formatting=do_formatting) if page else 1

        else:
                cli_ui.print_help_msg()
                return 1



if __name__ == "__main__":
        exit(main())
