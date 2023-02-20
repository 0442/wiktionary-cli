import tools.languages as languages
from services.db import Database

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
                #id = l[0]
                text = l[1] 
                datetime = l[2] 
                date = datetime.split(" ")[0]
                time = datetime.split(" ")[1]

                try:
                        date_groups[date].append((text,time))
                except:
                        date_groups[date] = [(text,time)]

        return date_groups

def print_saved_searches(do_formatting=True) -> int:
        """Print searches that are saved into the database
        """

        db = Database()
        searches = db.get_saved_searches()
        if not searches:
                print("No saved searches.")
                return 1

        if do_formatting:
                groups = __group_by_dates(searches)

                for date, searches in groups.items():
                        print("\033[1;31m" + date + "\033[m")
                        for s in searches:
                                output_str = "\033[35;2m" + "▏   " + s[1] + "\033[22;3m" + " " + f"\"{s[0]}\"" + "\033[0m" + "\033[0m"
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
                                output_str = "\033[35;2m" + "▏   " + p[1] + "\033[22m" + " " + f"{p[0]}" + "\033[0m" + "\033[0m"
                                print(output_str)
        else:
                for p in pages:
                        values = [ str(value) for value in list(p) ]
                        print("|".join(values))

        return 0