import re
from tools.wikiparser import Section
from time import sleep
from time import time
from tools import options
from tools import languages
from collections import namedtuple

Bracket = namedtuple('Bracket', ['pos', 'str'])
"""Position is the position of the starting/ending_bracket's first character's position in 'text'.
"""

# some utility functions

def _find_brackets(text: str, starting_bracket: str, ending_bracket: str) -> list[Bracket]:
        """
        Find brackets and their positions in a string.
        Returns brackets in the same order as they are found in the string.
        Returns a list of Brackets.
        """

        s_bracket_len = len(starting_bracket)
        e_bracket_len = len(ending_bracket)

        brackets = []
        for char_i in range(len(text)):
                if text[char_i : char_i + s_bracket_len] == starting_bracket:
                        brackets.append(Bracket(char_i, starting_bracket))
                elif text[char_i : char_i + e_bracket_len] == ending_bracket:
                        brackets.append(Bracket(char_i, ending_bracket))
        return brackets

def _is_overlapping(b1:Bracket, b2:Bracket) -> bool:
        """check if brackets, of more than 1 character, overlap.
        b1 and b2 are Brackets whose overlapping is to be tested.
        """
        result = False

        b1_left_pos = b1.pos # position of left most char
        b1_right_pos = b1.pos + len(b1.str) - 1 # position of right most char

        b2_left_pos = b2.pos # --||–-
        b2_right_pos = b2.pos + len(b2.str) - 1 # --||--

        if b2_left_pos <= b1_right_pos <= b2_right_pos:
                result = True

        if b1_left_pos <= b2_right_pos <= b1_right_pos:
                result = True

        return result


def _get_matching_brackets(brackets: list[Bracket], opening_bracket_str: str, closing_bracket_str: str, _used:dict=None, _pairs:list=None, _pointer:int=0, _has_no_pair:list=None, _iter_counter:int=0) -> list[Bracket]:
        """Returns a list of Brackets, where every opening bracket is followed by it's closing bracket.

        finds the pairs from the output of _find_brackets().

        Recursive function for matching closing and ending brackets from a list of brackets (including nested ones)
        """
        """Re-implemented _get_matching_bracket_positions.
        Only continues checking the brackets forward if there is a starting bracket for every closing bracket found. Otherwise stops going forwards."""
        start_time = time()

        # init stuff at first loop, at recursion depth 0.
        if _pairs == None:
                _pairs = []
        if _used == None:
                _used = {b:False for b in brackets}
        # _has_no_pair used for optimizing strings which include opening brackets that are not closed
        if _has_no_pair == None:
                _has_no_pair = {b:False for b in brackets}

        ending_pair = None
        starting_pair = brackets[_pointer] if _pointer < len(brackets) else None
        for cur_pointer in range(_pointer, len(brackets)):
                bracket = brackets[cur_pointer]

                # printing, for debugging
                if options.VERBOSE == True and options.PRINT_HELP:
                        print('\x1b[1F',end="")
                        for b in brackets:
                                if b in _pairs:
                                        print(f"\x1b[38;5;154;1m",end="")
                                elif _used[b] == True:
                                        print(f"\x1b[38;5;63m", end="")
                                elif _has_no_pair[b] == True:
                                        print(f"\x1b[38;5;124;4m", end="")
                                else:
                                        #print(f"\x1b[38;5;255m", end="")
                                        ...
                                print(b[1]+"\x1b[0m",end="")
                        print()

                        print("\x1b[0G"+80*" ", end="")
                        print(f"\x1b[{bracket.pos}G", end ="")
                        if _used[bracket]: print("\x1b[38;5;112m", end="")
                        if _has_no_pair[bracket]: print("\x1b[48;5;196m", end="")
                        print("^",end="")
                        print("\x1b[0m",end="")
                        print("\x1b[80G",end="", flush=True)
                        sleep(0.01)

                if _used[bracket] or _has_no_pair[bracket]:
                        continue

                if bracket.str == closing_bracket_str:
                        ending_pair = bracket
                        break

                if bracket.str == opening_bracket_str:
                        starting = bracket
                        _, ending = _get_matching_brackets(brackets, opening_bracket_str, closing_bracket_str, _used, _pairs, cur_pointer+1, _has_no_pair, _iter_counter)

                        if ending != None and _used[starting] != True and _used[ending] != True:
                                _pairs.append(starting)
                                _pairs.append(ending)
                                _used[starting] = True
                                _used[ending] = True
                                # overlapping ones can neither be used again
                                for b in brackets:
                                        if _is_overlapping(ending, b): _used[b] = True
                                        if _is_overlapping(starting, b): _used[b] = True

        if not ending_pair and starting_pair:
                _has_no_pair[starting_pair] = True
        if options.VERBOSE and _pointer == 0: print("bracket matching took:", round(time() - start_time, 5), "seconds")
        return _pairs, ending_pair


def find_bracketed_strings(text: str, starting_bracket: str, ending_bracket: str) -> tuple:
        """Finds the spans of bracketed substrings, including nested ones, in 'text'.

        Returns a list of spans.

        wrapper function for 'find_brackets' and 'get_matching_bracket_spans'
        """
        # if starting and ending brackets are the same, can't match them, dont try to find matching/nested ones
        br_spans = []
        if starting_bracket == ending_bracket:
                brackets = _find_brackets(text, starting_bracket, ending_bracket)
                if not brackets:
                        return []

                for i in range(0, len(brackets)-1, 2):
                        left = brackets[i]
                        left_pos = left.pos

                        right = brackets[i+1]
                        right_pos = right.pos + len(right.str)

                        br_spans.append((left_pos, right_pos))
        else:
                brackets = _find_brackets(text, starting_bracket, ending_bracket)
                matching_brackets,_ = _get_matching_brackets(brackets, starting_bracket, ending_bracket)
                for i in range(0,len(matching_brackets),2):
                        left_pos = matching_brackets[i].pos
                        right_pos = matching_brackets[i+1].pos + len(matching_brackets[i+1].str)
                        br_spans.append((left_pos, right_pos))

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
                indent_str = "\x1b[2m" + "▏   " + "\x1b[0m"
                #indent_str = "\x1b[2m" + "|   " + "\x1b[0m"

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
                                f_line = indent_count * indent_str + "\x1b[31m" + line.removeprefix(self_d*"#" + ":").strip() + "\x1b[39m"

                        # '#*' -lines (quotation title/source)
                        elif re.search("^" + (self_d)*"#" + "\*" + "[^#\:\*]+.*$", line):
                                f_line = indent_count * indent_str + "\x1b[3;31m" + line.removeprefix(self_d*"#" + "*").strip() + "\x1b[24;39m"
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

                formatted_str = "\x1b[2m"
                if "quote-book" in sections:
                        formatted_str += "(Quote book "
                elif "quote-journal" in sections:
                        formatted_str += "(Quote journal "
                elif "quote-web" in sections:
                        formatted_str += "(Quote web "
                elif "quote-text" in sections:
                        formatted_str += "(Quote text "

                formatted_str += f'"{title}", {year})\x1b[22m "{quote}"'
                return formatted_str

        if "Cite-web" in sections or ... in sections or ... in sections:
                ...

        sections.remove("en") if "en" in sections else None

        if "lb" in sections:
                sections.remove("lb")
                if options.COMPACT:
                        return ""

        # links?
        if "l" in sections:
                sections.remove("l")
                return "\x1b[31m" + ", ".join(sections) + "\x1b[39m"

        # examples?
        if "coi" in sections:
                sections.remove("coi")
                return "\x1b[3;31m" + ", ".join(sections) + "\x1b[23;39m"
        if "ux" in sections:
                sections.remove("ux")
                return "\x1b[3;31m" + ", ".join(sections) + "\x1b[23;39m"

        # wikipedia articles?
        if "w" in sections:
                return "\x1b[31m" + sections[len(sections)-1] + "\x1b[39m"


        formatted_str = "\x1b[3;31m(" + ", ".join(sections) + ")\x1b[23;39m"
        return formatted_str


def format_all_brackets(text: str, starting_bracket:str, ending_bracket:str, format_func: callable) -> str:
        """ Formats all brackets in text using the given function.

        'format_func' is passed a matching bracketed substring (with the brackets) from 'text' as an argument.
        'format_func' should output a new 'string' to be used as a replacement.

        Returns a modified copy of 'text'
        """
        start_time = time()

        mod_text = ""
        brackets = find_bracketed_strings(text, starting_bracket, ending_bracket)
        left_at = 0
        for b in brackets:
                target_bracket = b

                bracket_span = target_bracket[1]
                bracket_start = bracket_span[0]
                bracket_end = bracket_span[1]
                bracketed_str = target_bracket[0]

                replacement = format_func(bracketed_str)
                mod_text += text[ left_at : bracket_start] + replacement
                left_at = bracket_end
        mod_text += text[ left_at : ]

        end_time = time()
        if options.VERBOSE: print("formatting took:", end_time - start_time, "seconds")

        return mod_text


def format_section_content(section: Section, lang: str) -> str:
        """ Returns the text content of a section formatted into a nicer format.
        """

        sect_text = section.content
        # add section header
        sect_text = ("===" + "\x1b[1;34m" + section.title + "\x1b[22;39m" + "===" + '\n') + sect_text

        sect_text = _join_multiline_brackets(sect_text)

        sect_text = format_all_brackets(sect_text, "'''", "'''",
                lambda s: "\x1b[1m" + s.strip("'") + "\x1b[22m" )
        sect_text = format_all_brackets(sect_text, "<ref", "</ref>",
                lambda s: "" )
        sect_text = format_all_brackets(sect_text, "<ref", "/>",
                lambda s: "" )
        sect_text = format_all_brackets(sect_text, "<code", "</code>",
                lambda s: "" )
        sect_text = format_all_brackets(sect_text, "<code", "/>",
                lambda s: "" )
        sect_text = format_all_brackets(sect_text, "''", "''",
                lambda s: "\x1b[3m" + s.strip("'") + "\x1b[23m" )
        sect_text =  format_all_brackets(sect_text, "[[", "]]",
                lambda s: "\x1b[35m" + s.strip("[]") + "\x1b[39m" )
        sect_text = format_all_brackets(sect_text, "{{", "}}",
                format_curly_bracketed_str)

        sect_text = format_indents(sect_text)


        return sect_text
