from tools.wikiparser import *
from tools import languages
from tools import options
from tools.logger import log

from services.wiki_api import WikiApi
from services.db import Database

from ui import cli_ui

def _get_page_from_wiki(page_name: str, lang: str, site: str) -> WikiPage | None:
        """Get a page and create a WikiPage object from it.
        If unable to get the page, returns None.
        """
        wiki = WikiApi(lang, site)
        page_info = wiki.get_page(page_name)

        if not page_info:
                return None

        page_title = page_info[0]
        _page_id = page_info[1]
        page_text = page_info[2]

        page = WikiPage(page_text, page_title, lang, site)

        return page

def search_wiki(word:str, language:str, site:str) -> None:
        """Runs the command for searching a wiki page.
        Returns None.
        """
        db = Database()
        log(f"Saving search \"{word}, {site}, {language}\".")
        db.save_search(word, site, language)

        log(f"Searching wiki with \"{word}\".")
        wiki = WikiApi(language, site)
        results = wiki.search(word)
        if len(results) > 0:
                print("\n".join(results))

def fetch_wiki_page(word:str, language:str, path:str|None, site:str) -> None:
        """Runs the command for getting a page.
        Returns None.
        """
        if language not in languages.supported:
                print(f"Unsupported language: \"{language}\"\nSee the help message for supported languages.")
                return None

        db = Database()
        log(f"Saving search \"{word}, {site}, {language}\".")
        db.save_search(word, site, language)

        if not options.FORCE_WEB:
                log(f"Getting page from local database.")
                page_from_db = db.load_page(word, language, site)
        else:
                page_from_db = None

        if not page_from_db:
                log(f"Getting page from {site}.")
                page_from_web = _get_page_from_wiki(word, language, site)
                if not page_from_web:
                        cli_ui.not_found(word, language)
                        return
                log(f"Saving page {page_from_web.title}")
                db.save_page(page_from_web)

                cli_ui.print_sections(page_from_web, path)
        else:
                cli_ui.print_sections(page_from_db, path)

def list_saved_pages():
        """Command for listing saved pages.
        Returns None.
        """
        db = Database()
        pages = db.get_saved_pages()
        cli_ui.print_saved_pages(pages)

def list_saved_searches():
        """Command for listing saved searches.
        Returns None.
        """
        db = Database()
        searches = db.get_saved_searches()
        cli_ui.print_saved_searches(searches)

def help() -> None:
        """Command for printing the help message.
        Returns None."""
        cli_ui.print_help_msg()
