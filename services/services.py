from tools.wikiparser import *
from tools import languages
from tools import parsing_utils as parsing
from tools import config
from tools import options

from services.wiki_api import WikiApi
from services.db import Database

from ui import cli_ui

def __get_page_from_wiki(page_name:str, lang:str, site:str) -> WikiPage:
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

def __search_wiki(search:str, lang:str, site:str) -> int:
        wiki = WikiApi(lang, site)
        results = wiki.search(search)
        if not results:
                return 1
        [print(r) for r in results]
        return 0



def wiki_page(args:list[str], site:str) -> WikiPage | None:
        if len(args) < 2:
                cli_ui.print_help_msg()
                exit(1)
        
        lang = args[0]
        word = args[1]

        if lang not in languages.supported:
                print(f"Unsupported language: \"{lang}\"\nSee the help message for supported languages.")
                return None

        db = Database()
        db.save_search(word, "dictionary", lang)

        if options.do_search:
                __search_wiki(word, lang, site)
                return None

        # try to find the page from local db, else get it from wiki
        page = db.load_page(word, lang, site)

        if not page or options.force_web:
                page = __get_page_from_wiki(word, lang, site)
                if not page:
                        return None

                db.save_page(page)

        return page


"""
def translation(args:list[str]) -> int:
        if len(args) != 3:
                cli_ui.print_help_msg()
                exit(1)

        from_lang = args[0]
        to_lang = args[1]
        word = args[2]

        if from_lang == to_lang:
                print("Give two different languages for translation.")
                return 1

        if from_lang not in languages.supported or to_lang not in languages.supported:
                print(f"Unsupported language:",end="")
                if from_lang not in languages.supported:
                        print(f" \"{from_lang}\"",end="")
                if to_lang not in languages.supported:
                        print(f" \"{to_lang}\"",end="")
                print()

                return 1

        page = __get_page_from_wiki(word,from_lang,"wiktionary")
        tr_section_path = languages.abbrev_table[from_lang][from_lang] + "/Translations"
        sections = __get_matching_sections(page, tr_section_path, from_lang)

        tr = cli_ui.print_translations(sections, languages.abbrev_table[from_lang][to_lang])
        for k,v in tr.items():
                print(k)
                for t in v:
                        print(t)
"""