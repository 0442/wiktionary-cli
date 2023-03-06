import re
from tools.wikiparser import Section

# some utility functions

def _find_brackets(text: str, starting_bracket: str, ending_bracket: str) -> list[dict]:
        """
        Find brackets and their positions in a string.
        Returns brackets in the same order as they are found in the string.
        Returns a dictionary where 'string' is the matching bracket,
        'start' is the starting position of the bracket and 'end' is the ending position.
        'start' and 'end' will be the same if bracket length is 1, e.g. if matching agains '{' and '}'.
        """
        bracket_matches = list(re.finditer(f"({starting_bracket})" + "|" + f"({ending_bracket})", text))
        brackets = []
        for b in bracket_matches:
                brackets.append({
                        "string" : text[b.start() : b.end()],
                        "start" : b.start(),
                        "end" : b.end()
                })

        return brackets

def _get_matching_bracket_positions(brackets: list[dict], starting_bracket: str, ending_bracket: str) -> list[tuple]:
        """ Returns a list of starting and ending positions of matching brackets from the output of _find_brackets().

        recursive function for finding the starting and ending positions of matching brackets (including nested ones)
        """
        # remove backslashes, as bracket strings may include escaped characters for regex matching
        starting_bracket = starting_bracket.replace("\\", "")
        ending_bracket = ending_bracket.replace("\\", "")

        bracket_pairs = []
        if len(brackets) < 1:
                return bracket_pairs

        prev_brack = brackets.pop(0)

        while len(brackets) > 0:
                cur_brack = brackets.pop(0)

                # if opening bracket, continue to find it's closing one
                if cur_brack["string"] == starting_bracket and prev_brack["string"] == ending_bracket:
                        prev_brack = cur_brack
                        continue

                # if opening nested bracket, recurse
                if cur_brack["string"] == starting_bracket and prev_brack["string"] == starting_bracket:
                        brackets.insert(0, cur_brack)
                        nest_bracks = _get_matching_bracket_positions(brackets, starting_bracket, ending_bracket)
                        for b in nest_bracks: bracket_pairs.append(b)
                        prev_brack = cur_brack
                        continue

                # if closing brackets, add to matching pairs
                if cur_brack["string"] == ending_bracket and prev_brack["string"] == starting_bracket:
                        bracket_pairs.append( (prev_brack["start"], cur_brack["end"]) )
                        prev_brack = cur_brack
                        continue

                # if two closing brackets in a row, go break and go up a level in recursion
                if cur_brack["string"] == ending_bracket and prev_brack["string"] == ending_bracket:
                        break

        return bracket_pairs

def find_bracketed_strings(text: str, starting_bracket: str, ending_bracket: str) -> tuple:
        """Finds the spans of bracketed substrings, including nested ones, in 'text'.

        Returns a list of spans.

        wrapper function for 'find_brackets' and 'get_matching_bracket_spans'
        """
        # if starting and ending brackets are the same, can't match them, dont try to find matching/nested ones
        if starting_bracket == ending_bracket:
                brackets = _find_brackets(text, starting_bracket, ending_bracket)
                br_spans = []
                if brackets:
                        prev = brackets.pop(0)
                        while len(brackets) > 0:
                                cur = brackets.pop(0)
                                br_spans.append((prev["start"],cur["end"]))
                                prev = cur
        else:
                brackets = _find_brackets(text, starting_bracket, ending_bracket)
                br_spans = _get_matching_bracket_positions(brackets, starting_bracket, ending_bracket)

        bracketed_strs = []
        for span in br_spans:
                bracketed_strs.append( (text[span[0] : span[1]], span) )

        return bracketed_strs



def _join_multiline_brackets(text: str) -> str:
        """Returns a copy of 'text' where brackets that span over multiple lines are joined onto the same line.

        Some brackets' contents are split over multiple lines. Info inside brackets is often separated with '|'.
        Long bracketed strings are linebroken at these separators so that the following lines belonging inside these brackets start with '|'.
        This function joins these lines together.
        """
        lines = text.splitlines()

        if len(lines) < 1:
                return lines

        joined_lines = []
        prev_line = lines.pop(0)
        while len(lines) > 0:
                cur_line = lines.pop(0)
                if re.match("^[ \| }} \]\] ]", cur_line):
                        prev_line += cur_line
                        continue

                else:
                        joined_lines.append(prev_line)
                        prev_line = cur_line

        joined_lines.append(prev_line)

        return '\n'.join(joined_lines)



def format_indents(text: str) -> str:
        """Returns a copy of the text with indentation and line numbers added.
        """
        lines = text.splitlines()

        formatted_lines = []
        def indent_sub_sections(lines: list, formatted_lines: list, self_d: int = 1):
                """Recursively indent and linenumber definitions and their sub definitions.
                """
                indent_str = "\033[2m" + "▏   " + "\033[0m"
                #indent_str = "\033[2m" + "|   " + "\033[0m"

                linenum = 1
                while len(lines) > 0:
                        line = lines.pop(0).strip()
                        indent_count = self_d# + 1

                        # '##' -lines (sub definitions), recurse
                        if re.search("^" + (self_d+1)*"#" + "[^#\:\*]+.*$", line):
                                lines.insert(0,line)
                                indent_sub_sections(lines, formatted_lines, self_d + 1)
                                continue

                        # '#' -lines (definitions)
                        elif re.search("^" + (self_d)*"#" + "[^#\:\*]+.*$", line):
                                f_line = (indent_count-1) * indent_str + str(linenum) + ". " + line.removeprefix(self_d*"#").strip()
                                linenum += 1

                        # '#:' -lines (examples)
                        elif re.search("^" + (self_d)*"#" + "\:" + "[^#\:\*]+.*$", line):
                                f_line = indent_count * indent_str + "\033[31m" + line.removeprefix(self_d*"#" + ":").strip() + "\033[39m"

                        # '#*' -lines (quotation title/source)
                        elif re.search("^" + (self_d)*"#" + "\*" + "[^#\:\*]+.*$", line):
                                f_line = indent_count * indent_str + "\033[3;31m" + line.removeprefix(self_d*"#" + "*").strip() + "\033[24;39m"
                                continue # to exclude quotations

                        # '#:*' -lines (quotation itself)
                        elif re.search("^" + (self_d)*"#" + "\*\:" + "[^#\:\*]+.*$", line):
                                f_line = (indent_count+1) * indent_str + line.removeprefix(self_d*"#" + "*:").strip()
                                continue # to exclude quotations

                        # if line is a header, reset linenum
                        elif re.search("^===.*$", line):
                                f_line = line.strip("=")
                                linenum=1

                        # if line starts with other than '#', it doesn't need to be formatted here
                        elif re.search("^[^#]*$", line):
                                f_line = (indent_count - 1) * indent_str + line

                        # if line is higher level, break and return to go back up a level
                        else:
                                lines.insert(0,line)
                                break

                        formatted_lines.append(f_line)

                return formatted_lines

        return '\n'.join(indent_sub_sections(lines, formatted_lines))

def format_curly_bracketed_str(bracketed_str: str) -> str:
        sections = bracketed_str.strip("}{").split("|")

        # format quotes
        if "quote-book" in sections or "quote-journal" in sections or "quote-web" in sections or "quote-text" in sections:
                quote = ""
                year = ""
                title = ""
                for s in sections:
                        if s.startswith("passage="):
                                quote = s.removeprefix("passage=")
                        if s.startswith("title="):
                                title = s.removeprefix("title=")
                        if s.startswith("year="):
                                year = s.removeprefix("year=")

                formatted_str = "\033[2m"
                if "quote-book" in sections:
                        formatted_str += "(Quote book "
                elif "quote-journal" in sections:
                        formatted_str += "(Quote journal "
                elif "quote-web" in sections:
                        formatted_str += "(Quote web "
                elif "quote-text" in sections:
                        formatted_str += "(Quote text "

                formatted_str += f'"{title}", {year})\033[22m "{quote}"'
                formatted_str = ""
                return formatted_str

        # citations
        if "Cite-web" in sections or ... in sections or ... in sections:
                ...

        sections.remove("en") if "en" in sections else None
        sections.remove("lb") if "lb" in sections else None

        # links?
        if "l" in sections:
                sections.remove("l")
                return "\033[31m" + ", ".join(sections) + "\033[39m"

        # examples?
        if "coi" in sections:
                sections.remove("coi")
                return "\033[3;31m" + ", ".join(sections) + "\033[23;39m"
        if "ux" in sections:
                sections.remove("ux")
                return "\033[3;31m" + ", ".join(sections) + "\033[23;39m"

        # wikipedia articles?
        if "w" in sections:
                return "\033[31m" + sections[len(sections)-1] + "\033[39m"


        formatted_str = "\033[3;31m(" + ", ".join(sections) + ")\033[23;39m"
        return formatted_str


def format_all_brackets(text: str, starting_bracket:str, ending_bracket:str, format_func: callable) -> str:
        """ Formats all brackets in text using the given function.

        'format_func' is passed a matching bracketed substring (with the brackets) from 'text' as an argument.
        'format_func' should output a new 'string' to be used as a replacement.

        Returns a modified copy of 'text'
        """
        mod_text = text[:]
        brackets = find_bracketed_strings(text, starting_bracket, ending_bracket)
        while len(brackets) > 0:
                target_bracket = brackets[0]

                bracket_span = target_bracket[1]
                bracket_start = bracket_span[0]
                bracket_end = bracket_span[1]
                bracketed_str = target_bracket[0]

                replacement = format_func(bracketed_str)
                mod_text = mod_text[ : bracket_start] + replacement + mod_text[bracket_end : ]

                brackets = find_bracketed_strings(mod_text, starting_bracket, ending_bracket)

        return mod_text


def format_section_content(section: Section, lang: str) -> str:
        """ Returns the text content of a section formatted into a nicer format.
        """
        sect_text = section.content
        # add section header
        sect_text = ("===" + "\033[1;34m" + section.title + "\033[22;39m" + "===" + '\n') + sect_text

        sect_text = _join_multiline_brackets(sect_text)

        sect_text = format_all_brackets(sect_text, "'''", "'''",
                lambda s: "\033[1m" + s.strip("'") + "\033[22m" )
        sect_text = format_all_brackets(sect_text, "\<ref", "\<\/ref\>",
                lambda s: "" )
        sect_text = format_all_brackets(sect_text, "\<ref", "\/\>",
                lambda s: "" )
        sect_text = format_all_brackets(sect_text, "\<code", "\<\/code\>",
                lambda s: "" )
        sect_text = format_all_brackets(sect_text, "\<code", "\/\>",
                lambda s: "" )
        sect_text = format_all_brackets(sect_text, "''", "''",
                lambda s: "\033[3m" + s.strip("'") + "\033[23m" )
        sect_text =  format_all_brackets(sect_text, "\[\[", "\]\]",
                lambda s: "\033[35m" + s.strip("[]") + "\033[39m" )
        sect_text = format_all_brackets(sect_text, "{{", "}}",
                format_curly_bracketed_str)

        sect_text = format_indents(sect_text)

        return sect_text