from functools import reduce

#TODO add more options
# - option for including quotations in dictionary output
# - option for resolving redirects when getting page from wiki

VALID_OPTIONS = {
        ("-h", "--help") : "Show this screen and exit.", 
        ("-r", "--raw") : "Don't format output.", 
        ("-s", "--search") : "Search wiki instead of fetching a page.", 
        ("-f", "--force-web") : "Bypass attempts to find wanted page from local database.", 
        ("-ls", "--list-searches") : "Print saved searches and exit.",  
        ("-lp", "--list-pages") : "Print saved pages and exit.", 
        ("-v", "--verbose") : "Verbose output."
}

VALID_OPTIONS_LIST = reduce(lambda part, all: all + part, VALID_OPTIONS.keys())

def init(args:list[str]) -> int:
        global options
        global unknown_options

        options = [a for a in args if a.startswith("-")]
        unknown_options  = [opt for opt in options if opt not in valid_options_list]

        global do_formatting
        global do_search
        global list_searches
        global list_pages
        global force_web
        global print_help

        DO_FORMATTING = False if "-r" in OPTIONS or "--raw" in OPTIONS else True
        DO_SEARCH = True if "-s" in OPTIONS or "--search" in OPTIONS else False
        FORCE_WEB = True if "-f" in OPTIONS or "--force-web" in OPTIONS else False
        LIST_SEARCHES = True if "-ls" in OPTIONS or "--LIST-searches" in OPTIONS else False
        LIST_PAGES = True if "-lp" in OPTIONS or "--LIST-pages" in OPTIONS else False
        PRINT_HELP = True if "-h" in OPTIONS or "--help" in OPTIONS else False
        VERBOSE = True if "-v" in OPTIONS or "--verbose" in OPTIONS else False

        return 1 if UNKNOWN_OPTIONS else 0
