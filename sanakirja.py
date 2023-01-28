#!/bin/env python3

from pwiki.wiki import Wiki
from wikiparser import WikiParser, Section
import re
import sys 
import functools

word_classes = {
        "en" : ["Adjective", "Adverb", "Noun", "Verb"],
        "fi" : ["Adjektiivi", "Adverbi", "Substantiivi", "Verbi"],
        "ja" : [""],
        "sv" : [""]
}

supported_languages = ["en", "fi", "ja", "sv"]

# lookup tables for how languages used in eg. titles are written in wikipedia in different languages.
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
# for convenience
lang_in_own_lang = {
        "en" : "english",
        "fi" : "suomi",
        "ja" : "ja",
        "sv" : "svenska",
}


# Pages for some languages are formatted differently, thus multiple functions for parsing supported languages are given.
def format_en_sv_translations(tr_row: str, title: str) -> str:
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

        output_str = title + "\nFreq.\t|\tTranslation\n" + f"{8*'-'}+{5*8*'-'}\n" + output_str
        return  output_str.strip("\n")

def format_fi_ja_translations(tr_row: str) -> str:
        return f"Fancy formatting for translations from Finnish and Japanese not yet supported.\n\n{tr_row}"

# Functions for getting translations from wiktionary pages of certain languages, parsed into a printable format.
# Pages for some languages are formatted differently, thus multiple functions for supported languages are given.
def parse_fi_translations(page:Section, to_lang:str) -> str:
        try:
                finnish = page.find("Suomi")
                translations = []
                for wc in word_classes["fi"]:
                        sect = finnish.find(wc)
                        if sect:
                                content = sect.find("Käännökset").content.strip(" ").splitlines()
                                for l in content:
                                        translations.append(l)

                tr_line = ""
                for line in translations:
                        if langs_in_fi[to_lang] in line:
                                tr_line += line+'\n'

                return format_fi_ja_translations(tr_line)
        except:
                return None 

def parse_en_translations(page:Section, to_lang:str) -> str:
        try:
                full_str =""
                english = page.find("English")
                for wc in word_classes["en"]:
                        wc_sect = english.find(wc)
                        if wc_sect:
                                print(wc)
                                sect = wc_sect.find("Translations")
                                if sect:
                                        ls = sect.content.splitlines()
                                        for l in ls:
                                                print(l)
                                                if langs_in_en[to_lang] in l:
                                                        print(l)
                                                        full_str += format_en_sv_translations(l,wc) + "\n\n"
                return full_str
        except:
                return None

def parse_ja_translations(page:Section, to_lang:str) -> str:
        try:
                tr_row = page.find("").content.strip(" ")
                return format_fi_ja_translations(tr_row)
        except:
                return None

def parse_sv_translations(page:Section, to_lang:str) -> str:
        try:
                tr_row = page.find("").content.strip(" ")
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
        print("Usage: sanakirja [OPTION...] ARGS...")
        print("   or: sanakirja [OPTION...] -t TRANSLATE_FROM TRANSLATE_TO WORD")
        print("   or: sanakirja [OPTION...] -d LANGUAGE WORD [SECTION]")
        print("")
        print("Modes:")
        print("  -d, --dictionary\tget dictionary entry for word in given language")
        print("  -t, --translate \ttranslate word to given language")
        print("  -s, --synonyms  \tget synonyms for word in given language")
        print("  -h, --help      \tprint this help message")
        print("")
        print("Options:")
        print("  -r, --raw       \tdon't format output")
        print_supported_languages()

        return


def get_definitions(page:Section, lang:str):
        # combine lines from all word definitions + add headers
        def_lines = []
        for wc in word_classes[lang]:
                wc_sect = page.find(wc)
                if wc_sect:
                        content_lines = wc_sect.content.splitlines()
                        def_lines.append("===" + wc)
                        for line in content_lines:
                                def_lines.append(line)

        # strip irrelevant lines
        parsed_lines = []
        def_index = 1
        for line in def_lines:
                # if regular relevant line
                if re.search("\#[^\.\:\*]",line):# line.startswith("#"):
                        newline = str(def_index) + ". " + line.removeprefix("#")
                        parsed_lines.append(newline)
                        def_index += 1
                # if header
                elif line.startswith("==="):
                        newline = "\033[1;34m" + line.removeprefix("===") + "\033[0m"
                        parsed_lines.append("")
                        parsed_lines.append(newline)
                        def_index = 1
        
        # format '[[abcd]]'
        format_squares = []
        for line in parsed_lines:
                newline = ""
                for word in re.split("(\ |\.|\,)", line):
                        # find the beginning of [[]]
                        if word.find("[[")!=-1:
                                word = "\033[35m" + word.replace("[", "")
                        # find the end of [[]]
                        if word.find("]]")!=-1:
                                word = word.replace("]", "") + "\033[0m"

                        newline += word

                format_squares.append(newline)
        
        # format '{{a|b|c...}}'
        format_curlies = []
        for line in format_squares:
                newline = ""
                for word in re.split("(\ |\}\}|\{\{|\,|\.)", line):
                        # find the beginning of {{}}
                        if word.find("{{")!=-1:
                                word = "\033[3;31m" + word.replace("{{", "(")
                        # find the end of {}}
                        if word.find("}}")!=-1:
                                word = word.replace("}}", ")") + "\033[0m"

                        newline += word

                format_curlies.append(newline)
        
                

        
        return '\n'.join(format_curlies)
                                





def dict(args:list[str], do_formatting=True) -> int:
        if len(args) < 2:
                print_help_msg()
                exit(1)

        lang = args[0]
        word = args[1]


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
        parser = WikiParser(page_text,word)
        page = parser.page

        if len(args) >= 3:
                sect_path = args[2]
                sect = page.find(sect_path)
                if sect:
                        if do_formatting:
                                print(get_definitions(page.find(sect_path), lang))
                        else:
                                print(page.find(sect_path).content)
                else:
                        print(f"No section '{args[2]}'.")

        else:
                if do_formatting:
                        print(page)
                else:
                        print(page_text)

        return 0

def translate(args:list[str]) -> int:
        if len(args) != 3:
                print_help_msg()
                exit(1)

        from_lang = args[0]
        to_lang = args[1]
        word = args[2]

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
        parser = WikiParser(page_text, word)
        page = parser.page

        """
        # check if found page is for a word from the intended language
        page_language = titles[0]
        if page_language != lang_in_own_lang[from_lang]:
                word_not_found(word, from_lang)
                return 1
        """

        if from_lang == "fi":
                tr = parse_fi_translations(page, to_lang)
        elif from_lang == "en":
                tr = parse_en_translations(page, to_lang)
        elif from_lang == "ja":
                tr = parse_ja_translations(page, to_lang)
        elif from_lang == "sv":
                tr = parse_sv_translations(page, to_lang)

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
                # run in dictionary mode
                if opt in dict_option_names:
                        return dict(other_args, do_formatting = (False if "-r" in options else True))

                # run in translator mode
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