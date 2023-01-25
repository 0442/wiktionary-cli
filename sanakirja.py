#!/bin/env python3

from pwiki.wiki import Wiki
import re
import sys 
import functools

supported_languages = ["en", "fi", "ja", "sv"]

# lookup tables for how languages used in eg. titles are written in wikipedia in different languages.
lang_in_own_lang = {
        "en" : "english",
        "fi" : "suomi",
        "ja" : "ja",
        "sv" : "svenska",
}

langs_in_en = {
        "en" : "English",
        "fi" : "Finnish",
        "ja" : "Japanese",
        "sv" : "Swedish",
}

langs_in_fi = {
        "en" : "englanti",
        "fi" : "suomi",
        "ja" : "japani",
        "sv" : "ruotsi",
}

langs_in_ja = {
        "en" : "en",
        "fi" : "fi",
        "ja" : "ja",
        "sv" : "sv",
}

langs_in_sv = {
        "en" : "engelska",
        "fi" : "finska",
        "ja" : "japanska",
        "sv" : "svenska",
}

def format_en_sv_translations(tr_row: str) -> str:
        output_str = ""
        split = tr_row.split(": ")
        lang = split[0].strip(" *")
        entries = split[1].split("}}, ")

        for entry in entries:
                split = entry.split(" {{")

                raw_qualifier = "".join([i for i in split if "qualifier" in i])
                qualifier = ": ".join(raw_qualifier.strip("}{").split("|"))

                main_part = split[0].strip("}{")
                main_part = main_part.split("|")
                freq = main_part[0]
                lang = main_part[1]
                tr = ",".join(main_part[2:]).replace("tr=", " ")

                output_str += f"{freq}\t|\t{tr}\t\t{qualifier}\n"

        output_str = "Freq\t|\tTranslation\n" + f"{8*'-'}+{5*8*'-'}\n" + output_str
        return  output_str.strip("\n")

def format_fi_ja_translations(tr_row: str) -> str:
        return f"Fancy formatting for Finnish and Japanese not yet supported.\n{tr_row}"

# Functions for getting translations from wiktionary pages of certain languages, parsed into a printable format.
# Pages for some languages are formatted differently, thus a separate function for each supported language is given.
def parse_fi_translations(page_text:str, to_lang) -> str:
        try:
                tr_match = re.search(f"\*{langs_in_fi[to_lang]}: .*", page_text)
                tr_row = page_text[tr_match.start() : tr_match.end()]
                return format_fi_ja_translations(tr_row)
        except:
                return None 

def parse_en_translations(page_text:str, to_lang:str) -> str:
        try:
                translations = re.search(f"\* {langs_in_en[to_lang]}: .*", page_text)
                tr_row = page_text[translations.start() : translations.end()]
                return format_en_sv_translations(tr_row)
        except:
                return None

def parse_ja_translations(page_text:str, to_lang:str) -> str:
        try:
                translations = re.search("[^}.]*"+langs_in_ja[to_lang]+"\}\}.*", page_text)
                tr_row = page_text[translations.start() : translations.end()]
                return format_fi_ja_translations(tr_row)
        except:
                return None

def parse_sv_translations(page_text:str, to_lang:str) -> str:
        try:
                translations = re.search(f"\*{langs_in_sv[to_lang]}: .*", page_text)
                tr_row = page_text[translations.start() : translations.end()]
                return format_en_sv_translations(tr_row)
        except: 
                return None



# Functions for printing some output
def word_not_found(word:str, search_lang:str) -> None:
        print(f"Cannot find a wiktionary entry for '{word}' in {langs_in_en[search_lang]}.")
        return

def print_supported_languages() -> None:
        langs = [f"  {lang}\t{langs_in_en[lang]}" for lang in supported_languages]
        print()
        print("Supported languages:")
        print("\n".join(langs))
        print()
        return

def print_help_msg() -> None:
        print("Usage: sanakirja [OPTION] [ARGS]")
        print("   or: sanakirja [OPTION] -t [WORD] [TRANSLATE_FROM] [TRANSLATE_TO]")
        print("   or: sanakirja [OPTION] -d [WORD] [LANGUAGE]")
        print("")
        print("  -d, --dictionary\tget dictionary entry for word in given language")
        print("  -t, --translate \ttranslate word to given language")
        print("  -s, --synonyms  \tget synonyms for word in given language")
        print("  -h, --help      \tprint this help message")
        print("")
        return




def dict(args:list[str]) -> int:
        if len(args) != 2:
                print_help_msg()
                exit(1)

        word = args[0]
        lang = args[1]

        # check if user gave a usable language
        if lang not in supported_languages:
                print(f"Unsupported language: \"{lang}\"")
                print_supported_languages()
                return 1

        # form wiki link and object from chosen language
        wiki = Wiki(f'{lang}.wiktionary.org')

        # check if page exists
        if not wiki.exists(word):
                word_not_found(word, lang)
                return 1

        page_text = wiki.page_text(word)
        print(page_text)

        return 0

def translate(args:list[str]) -> int:
        if len(args) != 3:
                print_help_msg()
                exit(1)

        word = args[0]
        from_lang = args[1]
        to_lang = args[2]

        if from_lang == to_lang:
                print("Give two different languages for translation.")
                return 1
        # check if user gave a usable language
        if from_lang not in supported_languages or to_lang not in supported_languages:
                print(f"Unsupported language:",end="")
                if from_lang not in supported_languages:
                        print(f" \"{from_lang}\"",end="")
                if to_lang not in supported_languages:
                        print(f" \"{to_lang}\"",end="")
                print()

                print_supported_languages()
                return 1

        # form wiki link and object from chosen language
        wiki = Wiki(F"{from_lang}.wiktionary.org")

        # check if page exists
        if not wiki.exists(word):
                word_not_found(word, from_lang)
                return 1
        
        page_text = wiki.page_text(word)

        raw_titles = re.findall(f"=+[^=^\n.]+=+", page_text)
        titles = list(map(lambda t: t.strip("=}{").lower(), raw_titles))
        """
        # check if found page is for a word from the intended language
        page_language = titles[0]
        if page_language != lang_in_own_lang[from_lang]:
                word_not_found(word, from_lang)
                return 1
        """

        if from_lang == "fi":
                tr = parse_fi_translations(page_text, to_lang)
        elif from_lang == "en":
                tr = parse_en_translations(page_text, to_lang)
        elif from_lang == "ja":
                tr = parse_ja_translations(page_text, to_lang)
        elif from_lang == "sv":
                tr = parse_sv_translations(page_text, to_lang)

        if tr:
                print(tr)
        else:
                print(f"No translation from {langs_in_en[from_lang]} to {langs_in_en[to_lang]} found for \"{word}\".")

        return 0


def main() -> int:
        options = [arg for arg in sys.argv if arg.startswith("-")]
        other_args = [arg for arg in sys.argv[1:] if arg not in options]

        if len(options) < 1:
                print_help_msg()
                exit(1)

        # check and run function for given mode of operation option 
        translate_option_names = ["-t", "-tr", "-trans", "-translate"]
        dict_option_names = ["-d","-dict","-dictionary"]
        # iter all options and find the mode of operation option
        for opt in options:
                # run int dictionary mode
                if opt in dict_option_names:
                        return dict(other_args)

                # run int translator mode
                elif opt in translate_option_names:
                        return translate(other_args)

                # print help message
                elif opt == "-h" or opt == "--help":
                        print_help_msg()
                        return 0
                else:
                        print_help_msg()
                        return 1


if __name__ == "__main__":
        exit(main())