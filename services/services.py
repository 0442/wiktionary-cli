from tools.wikiparser import *
from tools import languages
from tools import parsing_utils as parsing
from tools import config
from tools import options

from services.wiki_api import WikiApi
from services.db import Database

from ui import cli_ui

def __get_page_from_wiki(page_name: str, lang: str, site: str) -> WikiPage:
        wiki = WikiApi(lang, site)
        page_info = wiki.get_page(page_name)

        if not page_info[0]:
                cli_ui.word_not_found(page_name, lang)
                return None

        page_title = page_info[0]
        page_id = page_info[1]
        page_text = page_info[2]

        page = WikiPage(page_text, page_title, lang, site)

        return page

def __search_wiki(search: str, lang: str, site: str) -> int:
        wiki = WikiApi(lang, site)
        results = wiki.search(search)
        if not results:
                return 1
        [print(r) for r in results]
        return 0

def wiki_page(args: list[str], site: str) -> WikiPage | None:
        if len(args) < 2:
                cli_ui.print_help_msg()
                exit(1)

        lang = args[0]
        word = args[1]

        if lang not in languages.supported:
                print(f"Unsupported language: \"{lang}\"\nSee the help message for supported languages.")
                return None

        db = Database()
        print(f"Saving search \"{word}, {site}, {lang}\".") if options.VERBOSE else None
        db.save_search(word, site, lang)

        if options.DO_SEARCH:
                print(f"Searching wiki with \"{word}\".") if options.VERBOSE else None
                __search_wiki(word, lang, site)
                return None

        # try to find the page from local db, else get it from wiki
        print(f"Attempting to get page from local database.") if options.VERBOSE else None
        page = db.load_page(word, lang, site)

        if not page or options.FORCE_WEB:
                print(f"Getting page from {site}.") if options.VERBOSE else None
                page = __get_page_from_wiki(word, lang, site)
                if not page:
                        return None

                print(f"Saving page {page.title}") if options.VERBOSE else None
                db.save_page(page)

        return page