import tools.languages as languages
from services.db import Database
from tools.wikiparser import *
import tools.parsing_utils as parsing

# Functions for printing some output
def word_not_found(word:str, search_lang:str) -> None:
        print(f"Cannot find a wiktionary entry for '{word}' in {languages.abbrev_table['en'][search_lang]}.")
        return

def print_supported_languages() -> None:
        langs = [f"  {lang}\t{languages.abbrev_table['en'][lang]}" for lang in languages.supported]
        print()
        print("Supported languages:")
        print("\n".join(langs))
        print()
        return

def print_help_msg() -> None:
        print("Wiktionary-cli - cli dictionary based on wiktionary entries.")
        print("")
        print("Usage:")
        print("  sanakirja dictionary|dict|d <lang> <title> [<section-path>|definitions|defs]")
        print("  sanakirja translate|tr|t <from-lang> <to-lang> <word>")
        print("  sanakirja article|wikipedia|wiki|w <lang> <title> [<section-path>]")
        print("")
        print("Options:")
        print("  -h --help            Show this screen.")
        print("  -r --raw             Don't format output.")
        print("  -s --search          Search wiki instead of fetching a page.")
        print("  -f --force-web       Get page from wiki and update local copy if saving is enabled in config.")
        print("  -ls --list-searches  Print saved searches and exit.")
        print("  -lp --list-pages     Print saved pages and exit.")
        print_supported_languages()
        return

def __group_by_dates(list:list[tuple]) -> dict:
        """Groups tuples with text and datetime into a dictionary by date as tuples containing text and time. 

        Util for nicer printing for print_saved_searches and print_saved_pages functions.
        """
        date_groups = {}
        for l in list:
                id = str(l[0])
                text = str(l[1])
                datetime = str(l[2])
                try:
                        count = str(l[3])
                except:
                        count = None

                date = datetime.split(" ")[0]
                time = datetime.split(" ")[1]

                try:
                        date_groups[date].append((id,text,time,count))
                except:
                        date_groups[date] = [(id,text,time,count)]

        return date_groups

def __group_consecutive_searches(searches:list[tuple]):
        """Groups similar consecutive searches and counts them for more compact output.
        """
        searches = searches.copy()
        grouped_searches = []

        prev_search = ("","")
        search_count = 1
        first_search_datetime = None

        while len(searches) > 0:
                cur_search = searches.pop(0)

                if cur_search[1] == prev_search[1]:
                        search_count += 1
                        prev_search = cur_search
                        continue
                else:
                        first_search_datetime = cur_search[2]
                        prev_search = cur_search

                grouped_searches.append((cur_search[0], cur_search[1], first_search_datetime, search_count))
                search_count = 1

        return grouped_searches



def print_saved_searches(do_formatting=True) -> int:
        """Print searches that are saved into the database
        """

        db = Database()
        searches = db.get_saved_searches()
        if not searches:
                print("No saved searches.")
                return 1

        if do_formatting:
                search_groups = __group_consecutive_searches(searches)
                date_groups = __group_by_dates(search_groups)

                for date, searches in date_groups.items():
                        print("\033[1;31m" + date + "\033[0m")
                        for s in searches:
                                id, text, time, count = s[0], s[1], ":".join(s[2].split(":")[:2]), s[3]
                                if count == "1":
                                        output_str = "\033[35;2m" + time + "\033[22m" + " " + f"{text}" + "\033[0m"
                                else:
                                        output_str = "\033[35;2m" + time + "\033[22m" + " " + f"{text}" + f"({count})" + "\033[0m"
                                print(output_str)
        else:
                for s in searches:
                        values = [ str(value) for value in list(s) ]
                        print("|".join(values))

        return 0
        
def print_saved_pages(do_formatting=True) -> int:
        """Print pages that are saved into the local database
        """

        db = Database()
        pages = db.get_saved_pages()
        if not pages:
                print("No saved searches.")
                return 1


        if do_formatting:
                groups = __group_by_dates(pages)

                for date, page_names in groups.items():
                        print("\033[1;31m" + date + "\033[m")
                        for p in page_names:
                                id,name,datetime = p[0], p[1], ":".join(p[2].split(":")[:2])
                                output_str = "\033[35;2m" + datetime + "\033[22m" + " " + f"{name}" + "\033[0m"
                                print(output_str)
        else:
                for p in pages:
                        values = [ str(value) for value in list(p) ]
                        print("|".join(values))

        return 0



def print_sections(sections:list[Section], lang, print_tree=False, do_formatting=True):
        if print_tree:
                for sect in sections:
                        print(sect)
                
                return 0


        for sect in sections:
                if do_formatting:
                        sect_str = parsing.format_section_content(sect, lang)
                else:
                        sect_str = sect.content

                print( sect_str+'\n\n' if sect_str is not None else "None", end="")

                return 0