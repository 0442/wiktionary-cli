from functools import reduce

#TODO add more OPTIONS
# - option for including quotations in dictionary output
# - option for resolving redirects when getting page from wiki

VALID_OPTIONS = {
        ("-h", "--help") : "Show this screen and exit.",
        ("-r", "--raw") : "Don't format output.",
        ("-s", "--search") : "Search wiki instead of fetching a page.",
        ("-f", "--force-web") : "Get wiki page from web without attempting to use a local copy first.",
        ("-ls", "--list-searches") : "Print saved searches and exit.",
        ("-lp", "--list-pages") : "Print saved pages and exit.",
        ("-v", "--verbose") : "Verbose output."
}

VALID_OPTIONS_LIST = reduce(lambda part,all: all+part, VALID_OPTIONS.keys())

def init(args: list[str]) -> int:
        global OPTIONS
        global UNKNOWN_OPTIONS

        OPTIONS = [a for a in args if a.startswith("-")]
        UNKNOWN_OPTIONS  = [opt for opt in OPTIONS if opt not in VALID_OPTIONS_LIST]

        global DO_FORMATTING
        global DO_SEARCH
        global LIST_SEARCHES
        global LIST_PAGES
        global FORCE_WEB
        global PRINT_HELP
        global VERBOSE

        DO_FORMATTING = False if "-r" in OPTIONS or "--raw" in OPTIONS else True
        DO_SEARCH = True if "-s" in OPTIONS or "--search" in OPTIONS else False
        FORCE_WEB = True if "-f" in OPTIONS or "--force-web" in OPTIONS else False
        LIST_SEARCHES = True if "-ls" in OPTIONS or "--list-searches" in OPTIONS else False
        LIST_PAGES = True if "-lp" in OPTIONS or "--list-pages" in OPTIONS else False
        PRINT_HELP = True if "-h" in OPTIONS or "--help" in OPTIONS else False
        VERBOSE = True if "-v" in OPTIONS or "--verbose" in OPTIONS else False

        return 1 if UNKNOWN_OPTIONS else 0