from tools.wikiparser import WikiParser, Section
from services.wiki_api import WikiApi
import ui.cli_ui as cli_ui
import tools.languages as languages
import tools.parsing_utils as parsing
import tools.config as config
from services.db import Database

def __get_page_from_wiki(page_name:str, lang:str, site:str) -> Section:
        wiki = WikiApi(lang, site)
        page_info = wiki.get_page(page_name)

        if not page_info[0]:
                cli_ui.word_not_found(page_name, lang)
                return 1
        
        page_title = page_info[0]
        page_id = page_info[1]
        page_text = page_info[2]

        page = WikiParser(page_text, page_title)

        return page

def __search_wiki(search:str, lang:str, site:str) -> int:
        wiki = WikiApi(lang, site)
        results = wiki.search(search)
        if not results:
                return 1
        [print(r) for r in results]
        return 0

def __get_matching_sections(page:WikiParser, target_path:str, lang:str) -> list[Section]:
        root_section = page.page_root_section

        matching_sections = []

        if not target_path:
                return []

        # if a section is given, print that section (or a group of sections, if target_path is a key word associated with some arbitrary group of sections, e.g. 'definitions', which matches Nouns, Verbs, etc..)
        if target_path.lower() == "definitions" or target_path.lower() == "defs":
                for wc in languages.definitions[lang]:
                        target_sect = root_section.find(languages.abbrev_table[lang][lang] + "/" + wc)
                        if target_sect:
                                matching_sections.append(target_sect)
                

        else:
                target_sect = root_section.find(target_path)
                if target_sect:
                        matching_sections.append(target_sect)


        if len(matching_sections) == 0:
                print(f"No sections found with \"{target_path}\"")
                return None
        else:
                return matching_sections



def dictionary(args:list[str], do_formatting=True, force_web=False, do_search=False) -> int:
        if len(args) < 2:
                cli_ui.print_help_msg()
                exit(1)
        
        lang = args[0]
        word = args[1]
        target_path = None
        if len(args) >= 3:
                target_path = args[2]
        else:
                target_path = "/"

        if lang not in languages.supported:
                print(f"Unsupported language: \"{lang}\"\nSee the help message for supported languages.")
                return 1

        db = Database()
        db.save_search(word)

        if do_search:
                return __search_wiki(word, lang, "wiktionary")

        # try to find the page from local db, else get it from wiki
        page = db.load_page(word)

        if not page or force_web:
                page = __get_page_from_wiki(word, lang, "wiktionary")
                db.save_page(page)

        matching_sects = __get_matching_sections(page, target_path, lang)
        if not matching_sects:
                return 1

        if target_path.endswith("/"):
                print_tree = True
        else:
                print_tree = False

        return cli_ui.print_sections(matching_sects, lang, print_tree=print_tree, do_formatting=do_formatting)


def wikipedia(args:list[str], do_formatting=True, force_web=False, do_search=False) -> int:
        # TODO implement database

        if len(args) < 2:
                cli_ui.print_help_msg()
                exit(1)
        
        lang = args[0]
        title = args[1]
        target_path = None
        if len(args) >= 3:
                target_path = args[2]
        
        if lang not in languages.supported:
                print(f"Unsupported language: \"{lang}\"")
                return 1

        if do_search:
                return __search_wiki(title, lang, "wikipedia")
        
        page = __get_page_from_wiki(title, lang, "wiktionary")

        matching_sects = __get_matching_sections(page, target_path, lang)
        if not matching_sects:
                return 1

        if target_path.endswith("/"):
                print_tree = True
        else:
                print_tree = False

        return cli_ui.print_sections(matching_sects, lang, print_tree=print_tree, do_formatting=do_formatting)



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