from tools.wikiparser import WikiParser
from pwiki.wiki import Wiki
import ui.cli_ui as cli_ui
import tools.languages as languages
import tools.parsing_utils as parsing
import tools.config as config
from services.db import Database

# TODO: split functions into smaller chunks.

def get_wiki_page(args:list[str], do_formatting=True) -> int:
        if len(args) < 2:
                cli_ui.print_help_msg()
                exit(1)
        
        lang = args[0]
        title = args[1]
        sect_path = None
        if len(args) >= 3:
                sect_path = args[2]
        
        # check if user gave a usable language
        if lang not in languages.supported:
                print(f"Unsupported language: \"{lang}\"")
                #print_languages.supported()
                return 1


        wiki = Wiki(f'{lang}.wikipedia.org')
        
        # check if page exists
        if not wiki.exists(title):
                cli_ui.word_not_found(title, lang)
                return 1
        
        page_text = wiki.page_text(title)
        page = WikiParser(page_text,title)

        root_sect = page.page_root_section

        if sect_path:
                sect = root_sect.find(sect_path)
                if sect:
                        if do_formatting:
                                print(parsing.format_section_content(sect, lang))
                        else:
                                print(sect.content)
                else:
                        print(f"No section '{args[2]}'.")
                        return 0
        # if no section given, print root_section (__str__(), page's structure)
        else:
                if do_formatting:
                        print(root_sect)
                else:
                        print(page_text)

        return 0


def get_dictionary_entry(args:list[str], do_formatting=True) -> int:

        if len(args) < 2:
                cli_ui.print_help_msg()
                exit(1)
        
        lang = args[0]
        word = args[1]
        sect_path = None
        if len(args) >= 3:
                sect_path = args[2]

        # check if user gave a usable language
        if lang not in languages.supported:
                print(f"Unsupported language: \"{lang}\"\nSee the help message for supported languages.")
                #print_languages.supported()
                return 1


        # try to find the page from local db, else get it from wiki + save search
        db = Database()
        db.save_search(word)
        page = db.load_page(word)

        if not page:
                # form wiki link and object from chosen language
                wiki = Wiki(f'{lang}.wiktionary.org')

                # check if page exists
                if not wiki.exists(word):
                        cli_ui.word_not_found(word, lang)
                        return 1

                page_text = wiki.page_text(word)
                page_title = wiki.normalize_title(word)
                page = WikiParser(page_text,page_title)
                root_sect = page.page_root_section
                db.save_page(page)
        else:
                root_sect = page.page_root_section


        # if a section is given, print that section (or a group of sections, if sect_path is a key word associated with some arbitrary group of sections, e.g. 'definitions', which matches Nouns, Verbs, etc..)
        if sect_path:
                if sect_path.lower() == "definitions" or sect_path.lower() == "defs":
                        for wc in languages.definitions[lang]:
                                sect = root_sect.find(languages.abbrev_table[lang][lang]+ "/" + wc)
                                if sect:
                                        if do_formatting:
                                                sect_str = parsing.format_section_content(sect, lang)
                                        else:
                                                sect_str = sect.content

                                        print( sect_str+'\n\n' if sect_str is not None else "None", end="")

                else:
                        sect = root_sect.find(sect_path)
                        if sect:
                                if do_formatting:
                                        print(parsing.format_section_content(sect, lang))
                                else:
                                        print(sect.content)
                        else:
                                print(f"No section '{args[2]}'.")
                                return 1

        # if no section given, print whole page(either root_sect.__str__() or the raw text, if command was run with option '-r' )
        else:
                if do_formatting:
                        print(root_sect)
                else:
                        print(page.page_text)

        return 0


def translate_word(args:list[str]) -> int:
        if len(args) != 3:
                cli_ui.print_help_msg()
                exit(1)

        from_lang = args[0]
        to_lang = args[1]
        word = args[2]

        if from_lang == to_lang:
                print("Give two different languages for translation.")
                return 1
        # check if user gave a usable language
        if from_lang not in languages.supported or to_lang not in languages.supported:
                print(f"Unsupported language:",end="")
                if from_lang not in languages.supported:
                        print(f" \"{from_lang}\"",end="")
                if to_lang not in languages.supported:
                        print(f" \"{to_lang}\"",end="")
                print()

                #print_languages.supported()
                return 1

        # form wiki link and object from chosen language
        wiki = Wiki(F"{from_lang}.wiktionary.org")

        # check if page exists
        if not wiki.exists(word):
                cli_ui.word_not_found(word, from_lang)
                return 1
        
        page_text = wiki.page_text(word)
        parser = WikiParser(page_text, word)
        page = parser.page

        tr_str = ""
        if from_lang == "fi":
                for wc in languages.definitions[from_lang]:
                        tr_section = parser.find(f"{word}/{languages.abbrev_table[from_lang][from_lang].capitalize()}/{wc}/Käännökset", from_lang).content
                        if not tr_section:
                                continue
                        tr_str += wc + '\n\n'
                        tr_str += "\n".join([line.removeprefix(f"*{languages.abbrev_table[from_lang][to_lang]}: ") for line in tr_section.splitlines() if line.startswith(f"*{languages.abbrev_table[from_lang][to_lang]}")])

        elif from_lang == "en":
                full_str = ""
                for wc in languages.definitions[from_lang]:
                        path=f"{word}/{languages.abbrev_table[from_lang][from_lang]}/{wc}/Translations"
                        tr_section = page.find(path)
                        if not tr_section:
                                continue
                        full_str += wc + '\n\n'
                        full_str += parser.parse_translations_section(parser.format_section_content(path,to_lang),from_lang,to_lang)
                tr_str = full_str

        if tr_str:
                print(tr_str)
        else:
                print(f"No translation from {languages.abbrev_table['en'][from_lang]} to {languages.abbrev_table['en'][to_lang]} found for \"{word}\".")

        return 0