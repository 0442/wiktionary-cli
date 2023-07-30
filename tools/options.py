from functools import reduce
from sys import argv

DICTIONARY_COMMAND_NAMES = ["d", "dictionary"]
ARTICLE_COMMAND_NAMES = ["a", "article", "wikipedia"]

VALID_OPTIONS = {
        ("-h", "--help") : "Print this message and exit.",
        ("-r", "--raw") : "Don't format output.",
        ("-s", "--search") : "Do a search instead of fetching a page.",
        ("-f", "--force-web") : "Fetch page from wiki even if a local copy exists.",
        ("-ls", "--list-searches") : "Print saved searches and exit.",
        ("-lp", "--list-pages") : "Print saved pages and exit.",
        ("-c", "--compact") : "Output pages in a more compact format.",
        ("-v", "--verbose") : "Verbose output.",
}

VALID_OPTIONS_LIST = reduce(lambda o,l: o+l, VALID_OPTIONS.keys())

def init() -> None:
        """Sets some constants from command line arguments.
        Raises errors if arguments are invalid.
        Returns None.
        """
        global POSITIONAL_ARGS
        global OPTIONS
        global UNKNOWN_OPTIONS

        POSITIONAL_ARGS = [a for a in argv[1:] if a not in VALID_OPTIONS_LIST]
        OPTIONS = [a for a in argv[1:] if a.startswith("-")]
        UNKNOWN_OPTIONS  = [opt for opt in OPTIONS if opt not in VALID_OPTIONS_LIST]

        global DO_FORMATTING
        global DO_SEARCH
        global LIST_SEARCHES
        global LIST_PAGES
        global FORCE_WEB
        global PRINT_HELP
        global VERBOSE
        global COMPACT

        DO_FORMATTING = False if "-r" in OPTIONS or "--raw" in OPTIONS else True
        DO_SEARCH = True if "-s" in OPTIONS or "--search" in OPTIONS else False
        FORCE_WEB = True if "-f" in OPTIONS or "--force-web" in OPTIONS else False
        LIST_SEARCHES = True if "-ls" in OPTIONS or "--list-searches" in OPTIONS else False
        LIST_PAGES = True if "-lp" in OPTIONS or "--list-pages" in OPTIONS else False
        PRINT_HELP = True if "-h" in OPTIONS or "--help" in OPTIONS else False
        VERBOSE = True if "-v" in OPTIONS or "--verbose" in OPTIONS else False
        COMPACT = True if "-c" in OPTIONS or "--compact" in OPTIONS else False

        if UNKNOWN_OPTIONS:
                raise Exception(f'Unkown options: {", ".join(UNKNOWN_OPTIONS)}')
        elif len(POSITIONAL_ARGS) < 3:
                raise Exception('Not enough arguments.')
        elif len(POSITIONAL_ARGS) > 4:
                raise Exception('Too many arguments.')
        elif POSITIONAL_ARGS[0] not in DICTIONARY_COMMAND_NAMES and POSITIONAL_ARGS[0] not in ARTICLE_COMMAND_NAMES:
                raise Exception('Invalid arguments.')

