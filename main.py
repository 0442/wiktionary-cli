#!/bin/env python3
from services import commands
from tools import options

def main() -> int:
        try:
                options.init()
        except Exception as e:
                print(e)
                commands.help()
                return 1

        if options.PRINT_HELP:
                commands.help()
                return 0
        elif options.LIST_SEARCHES:
                commands.list_saved_searches()
                return 0
        elif options.LIST_PAGES:
                commands.list_saved_pages()
                return 0

        command = options.POSITIONAL_ARGS[0]
        language = options.POSITIONAL_ARGS[1]
        word = options.POSITIONAL_ARGS[2]
        # optional arg
        path = options.POSITIONAL_ARGS[3] if len(options.POSITIONAL_ARGS) == 4 else None

        if command in options.DICTIONARY_COMMAND_NAMES:
                site = "wiktionary"
        elif command in options.ARTICLE_COMMAND_NAMES:
                site = "wikipedia"

        if options.DO_SEARCH:
                commands.search_wiki(word, language, site)
        else:
                commands.fetch_wiki_page(word, language, path, site)

        return 0

if __name__ == "__main__":
        exit(main())
