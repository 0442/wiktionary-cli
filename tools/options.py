from functools import reduce

#TODO add more options
# - option for including quotations in dictionary output
# - option for resolving redirects when getting page from wiki

valid_options = {
        ("-h", "--help") : "Show this screen and exit.", 
        ("-r", "--raw") : "Don't format output.", 
        ("-s", "--search") : "Search wiki instead of fetching a page.", 
        ("-f", "--force-web") : "Bypass attempts to find wanted page from local database.", 
        ("-ls", "--list-searches") : "Print saved searches and exit.",  
        ("-lp", "--list-pages") : "Print saved pages and exit.", 
        ("-v", "--verbose") : "Verbose output."
}

valid_options_list = reduce(lambda part,all: all+part, valid_options.keys())

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

        do_formatting = False if "-r" in options or "--raw" in options else True
        do_search = True if "-s" in options or "--search" in options else False
        force_web = True if "-f" in options or "--force-web" in options else False
        list_searches = True if "-ls" in options or "--list-searches" in options else False
        list_pages = True if "-lp" in options or "--list-pages" in options else False
        print_help = True if "-h" in options or "--help" in options else False

        return 1 if unknown_options else 0