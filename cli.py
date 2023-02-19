#!/bin/env python3

import sys 
from time import sleep
import sys
import ui.cli_ui as cli_ui
import services.services as services
from services.db import Database

def main() -> int:
        #TODO add more options, e.g. one for including quotations
        # extract options and other, positional arguments
        options = [opt for opt in sys.argv if opt.startswith("-")]
        positional_args = [arg for arg in sys.argv[1:] if arg not in options] 

        # check for invalid options
        valid_options = ["-r", "--raw", "-h", "--help", "-s", "--searches", "-p", "--pages"]
        invalid_opts  = [opt for opt in options if opt not in valid_options]
        print( f"Invalid options: { ', '.join(invalid_opts) }.\n" ) if len(invalid_opts) > 0 else None

        # handle options
        if "-h" in options or "--help" in options:
                cli_ui.print_help_msg()
                return 0

        if "-s" in options or "--searches" in options:
                db = Database()
                ss = db.get_saved_searches()
                if ss:
                    for s in ss:
                        print(s)
                    return 0
                else:
                    return 1

        if "-p" in options or "--pages" in options:
                db = Database()
                s = db.get_saved_pages()
                if s:
                    print(s)
                    return 0
                else:
                    return 1


        # check and run function for given mode
        translate_mode_names = ["t", "tr", "translate"]
        dict_mode_names = ["d", "dict", "dictionary"]
        wiki_mode_names = ["w", "wiki", "wikipedia"]

        # run in dictionary mode
        if positional_args[0] in dict_mode_names:
                return services.get_dictionary_entry(positional_args[1:], do_formatting = (False if "-r" in options or "--raw" in options else True))
        # run in translator mode
        elif positional_args[0] in translate_mode_names:
                return services.translate_word(positional_args[1:])
        # run in wikipedia mode 
        elif positional_args[0] in wiki_mode_names:
                return services.get_wiki_page(positional_args[1:])
        else:
                cli_ui.print_help_msg()
                return 1


if __name__ == "__main__":
        exit(main())
