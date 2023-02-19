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
        print("Wiktionary-cli - cli dictionary and translator based on wiktionary entries.")
        print("")
        print("Usage:")
        print("  sanakirja dictionary|dict|d <lang> <title> [<section-path>|definitions|defs]")
        print("  sanakirja article|wikipedia|wiki|w <lang> <title> [<section-path>]")
        print("  sanakirja translate|tr|t <from-lang> <to-lang> <word>")
        print("")
        print("Options:")
        print("  -h --help      Show this screen.")
        print("  -r --raw       Don't format output.")
        print("  -s --searches  Print saved searches")
        print("  -p --pages     Print saved pages")
        print_supported_languages()

        return

def print_saved_searches():
        db = Database()
        ss = db.get_saved_searches()
        if ss:
                for s in ss:
                        print(s)
                return 0
        else:
                return 1

def print_saved_pages():
        db = Database()
        s = db.get_saved_pages()
        if s:
                print(s)
                return 0
        else:
                return 1