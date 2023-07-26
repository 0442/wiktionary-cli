import tools.languages as languages
from services.db import Database
from tools.wikiparser import WikiPage, Section
import tools.parsing_utils as parsing
from tools import options

# Functions for printing some output
def word_not_found(word: str, search_lang: str) -> None:
        print(f"Cannot find a wiktionary entry for '{word}' in {languages.abbrev_table['en'][search_lang]}.")
        return None

def print_supported_languages() -> None:
        print("Supported languages: ")
        for l in languages.supported:
                print(f"  {l}")
        return None

def print_keywords() -> None:
        keywords = WikiPage.search_keywords

        print("Keywords:")
        for _,k in keywords.items():
                print("  ", end="")
                print(" ".join(k))

        return None

def print_path_explanation() -> None:
        print("Section path: ")
        print('  Either the wanted section\'s name, or a "." separated list of section names/numbers to the wanted section.')
        print('  If section-path starts with ".", path is walked from root. Otherwise from first occurence of first part of path.')
        print('  If section-path ends with ".", matching section\'s structure is printed. Otherwise it\'s content is printed.')

def print_options() -> None:
        print(f"Options:")
        for opt_names, opt_desc in options.VALID_OPTIONS.items():
                options_str = " ".join(opt_names)
                left_offset = (21 - len(options_str)) * " "
                print("  " + options_str + left_offset + opt_desc)

def print_help_msg() -> None:
        dict_commands = "|".join(options.DICTIONARY_MODE_NAMES)
        article_commands = "|".join(options.ARTICLE_MODE_NAMES)

        print("Usage:")
        print(f"  wiktionary {dict_commands} <language> <title> [<section-path>|<keyword>]")
        print(f"  wiktionary {article_commands} <from-language> <to-language> <word>")
        print()
        print_options()
        print()
        print_supported_languages()
        print()
        print_keywords()
        print()
        print_path_explanation()
        return None

def print_saved_searches() -> int:
        """Print searches that are saved into the database
        """

        db = Database()
        searches = db.get_saved_searches()
        if not searches:
                print("No saved searches.")
                return 1

        if options.DO_FORMATTING:
                search_groups = _group_consecutive_searches(searches)
                date_groups = _group_by_dates(search_groups)

                for date, srchs in date_groups.items():
                        print("\033[1;31m" + date + "\033[0m")
                        for s in srchs:
                                id, text, time, count = s[0], s[1], ":".join(s[2].split(":")[: 2]), s[3]
                                if count == "1":
                                        output_str = "\033[35;2m" + time + "\033[22m" + " " + f"{text}" + "\033[0m"
                                else:
                                        output_str = "\033[35;2m" + time + "\033[22m" + " " + f"{text}" + f"({count})" + "\033[0m"
                                print(output_str)

                print("count:", len(searches))
        else:
                for s in searches:
                        values = [ str(value) for value in list(s) ]
                        print("|".join(values))

        return 0

def print_saved_pages() -> int:
        """Print pages that are saved into the local database
        """

        db = Database()
        pages = db.get_saved_pages()
        if not pages:
                print("No saved searches.")
                return 1


        if options.DO_FORMATTING:
                groups = _group_by_dates(pages)

                for date, page_names in groups.items():
                        print("\033[1;31m" + date + "\033[m")
                        for p in page_names:
                                id,name,datetime = p[0], p[1], ":".join(p[2].split(":")[: 2])
                                output_str = "\033[35;2m" + datetime + "\033[22m" + " " + f"{name}" + "\033[0m"
                                print(output_str)

                print("count:", len(pages))
        else:
                for p in pages:
                        values = [ str(value) for value in list(p) ]
                        print("|".join(values))

        return 0

def print_sections(page: WikiPage, path: str):
        # Only print page structure (__str__ of page's root section) when no path given
        if not path:
                if not options.DO_FORMATTING:
                        print(page.root_section)
                        return 0

                text = page.root_section.__str__()
                print(parsing.format_indents(text))
                return 0

        matching_sects = page.find_page_sections(path)

        if not matching_sects:
                print(f"No matching sections for \"{path}\"")
                return 1

        # when path ends in '/', print matching sections' subsection structures
        if path.endswith("/"):
                for s in matching_sects:
                        text = s.__str__()
                        if options.DO_FORMATTING:
                                print(parsing.format_indents(text))
                        else:
                                print(text)
                return 0

        for sect in matching_sects:
                if options.DO_FORMATTING:
                        sect_str = parsing.format_section_content(sect, page.language)
                else:
                        sect_str = sect.content

                print(sect_str + '\n\n' if sect_str is not None else "None", end="")

        return 0

# move section parsing elsewhere and add printing here.
def print_translations(sections: list[Section], target_lang: str) -> dict:
        translations = {}
        for s in sections:

                lines = s.content.splitlines()
                cur_tr_top = ""
                for l in lines:
                        if l.strip().startswith("{{trans-top"):
                                cur_tr_top = l
                                translations[cur_tr_top] = []
                                continue
                        elif l.strip().startswith("{{trans-bottom"):
                                cur_tr_top = ""
                                continue
                        elif l.strip(" *").startswith(target_lang):
                                translations[cur_tr_top].append(l)

        return translations




def _group_by_dates(list: list[tuple]) -> dict:
        """Groups tuples with id, text, datetime and count, into a dictionary by date id, text, time and count.

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

def _group_consecutive_searches(searches: list[tuple]):
        """Groups similar consecutive searches and counts them for more compact output.
        """
        srchs = searches.copy()
        grouped_searches = []

        prev_search = srchs.pop(0)
        first_search_datetime = prev_search[2]
        search_count = 1

        while len(srchs) > 0:
                cur_search = srchs.pop(0)

                if cur_search[1] == prev_search[1]:
                        search_count += 1
                        prev_search = cur_search
                        continue

                grouped_searches.append((prev_search[0], prev_search[1], first_search_datetime, search_count))
                prev_search = cur_search
                first_search_datetime = prev_search[2]
                search_count = 1

        grouped_searches.append((cur_search[0], cur_search[1], cur_search[2], search_count))

        return grouped_searches
