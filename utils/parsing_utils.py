import re
from utils.wikiparser import Section

# some utility functions

def __find_brackets(line:str, starting_bracket:str, ending_bracket:str) -> list[dict]:
        """
        Find brackets and their positions in a string.
        Returns brackets in the same order as they are found in the string.
        Returns a dictionary where 'string' is the matching bracket, 
        'start' is the starting position of the bracket and 'end' is the ending position.
        'start' and 'end' will be the same if bracket length is 1, e.g. if matching agains '{' and '}'.
        """
        bracket_matches = list(re.finditer(f"({starting_bracket})" + "|" + f"({ending_bracket})", line))
        brackets = []
        for b in bracket_matches:
                brackets.append({
                        "string" : line[b.start() : b.end()],
                        "start" : b.start(),
                        "end" : b.end()
                })

        return brackets

def __get_matching_bracket_positions(brackets:list[dict], starting_bracket:str, ending_bracket:str) -> list[tuple]:
        """ Returns a list of starting and ending positions of matching brackets from the output of __find_brackets().

        recursive function for finding the starting and ending positions of matching brackets (including nested ones)
        """
        # brackets may included characters that needed to be escaped for regex, so remove the backslashes
        starting_bracket = starting_bracket.replace("\\", "")
        ending_bracket = ending_bracket.replace("\\", "")

        bracket_pairs = []
        if len(brackets) < 1:
                return bracket_pairs

        prev_brack = brackets.pop(0)

        while len(brackets) > 0:
                curr_brack = brackets.pop(0)

                # if opening bracket, continue to find it's closing one
                if curr_brack["string"] == starting_bracket and prev_brack["string"] == ending_bracket:
                        prev_brack = curr_brack
                        continue

                # if opening nested bracket, recurse
                if curr_brack["string"] == starting_bracket and prev_brack["string"] == starting_bracket:
                        brackets.insert(0, curr_brack)
                        nest_bracks = __get_matching_bracket_positions(brackets, starting_bracket, ending_bracket)

                        [bracket_pairs.append(b) for b in nest_bracks]
                        prev_brack = curr_brack
                        continue

                # if closing brackets, add to matching pairs
                if curr_brack["string"] == ending_bracket and prev_brack["string"] == starting_bracket:
                        bracket_pairs.append( (prev_brack["start"], curr_brack["end"]) )
                        prev_brack = curr_brack
                        continue
                
                # if two closing brackets in a row, go break and go up a level in recursion
                if curr_brack["string"] == ending_bracket and prev_brack["string"] == ending_bracket:
                        break

        return bracket_pairs

def find_bracketed_strings(string:str, starting_bracket:str, ending_bracket:str) -> tuple:
        """ 
        Wraps 'find_brackets' and 'get_matching_bracket_spans' 
        for finding all bracketed strings and their spans, 
        including nested ones, in a string.
        """
        # if starting and ending brackets are the same, can't match them, dont try to find matching/nested ones
        if starting_bracket == ending_bracket:
                brackets = __find_brackets(string, starting_bracket, ending_bracket)
                br_spans = []
                if brackets:
                        prev = brackets.pop(0)
                        while len(brackets) > 0:
                                curr = brackets.pop(0)
                                br_spans.append((prev["start"],curr["end"]))
                                prev = curr
        else:
                brackets = __find_brackets(string, starting_bracket, ending_bracket)
                br_spans = __get_matching_bracket_positions(brackets, starting_bracket, ending_bracket)

        bracketed_strs = []
        for span in br_spans:
                bracketed_strs.append( (string[span[0] : span[1]], span) )

        return bracketed_strs



def __join_multiline_brackets(lines:list) -> list:
        """Returns a copy of lines where brackets that span over multiple lines are joined onto the same line. 
        
        Some brackets' contents are split over multiple lines. Info inside brackets is often separated with '|'. 
        Long bracketed strings are linebroken at these separators so that the following lines belonging inside these brackets start with '|'.
        This function joins these lines together.
        """
        lines = lines.copy()

        if len(lines) < 1:
                return lines

        formatted_lines = []
        prev_line = lines.pop(0)
        while len(lines) > 0:
                curr_line = lines.pop(0)
                if curr_line.startswith("|"):
                        prev_line += curr_line
                        continue
                
                else:
                        formatted_lines.append(prev_line)
                        prev_line = curr_line

        formatted_lines.append(prev_line)

        return formatted_lines
        


def __format_indents(lines:list) -> list:
        """Returns a copy of the lines of a wiki page with indentation and line numbers added.
        """
        lines = lines.copy()

        formatted_lines = []
        def indent_sub_sections(lines:list, formatted_lines:list, self_d:int=1):
                """Recursively indent and linenumber definitions and their sub definitions.
                """
                #indent_str = "▏   "
                indent_str = "|   "

                linenum = 1
                while len(lines) > 0:
                        line = lines.pop(0)

                        # '##' -lines (sub definitions), recurse
                        if re.search("^" + (self_d+1)*"#" + "[^#\:\*]+.*$", line):
                                lines.insert(0,line)
                                indent_sub_sections(lines, formatted_lines, self_d + 1)
                                continue

                        # '#' -lines (definitions)
                        elif re.search("^" + (self_d)*"#" + "[^#\:\*]+.*$", line):
                                f_line = (self_d-1)*("\033[2m" + indent_str + "\033[0m") + str(linenum) + "." + line.removeprefix(self_d*"#")
                                linenum += 1

                        # '#:' -lines (examples)
                        elif re.search("^" + (self_d)*"#" + "\:" + "[^#\:\*]+.*$", line):
                                f_line = (self_d)*("\033[2m"+indent_str+"\033[0m") + "\033[31m" + line.removeprefix(self_d*"#" + ":") + "\033[39m"

                        # '#*' -lines (quotation title/source)
                        elif re.search("^" + (self_d)*"#" + "\*" + "[^#\:\*]+.*$", line):
                                f_line = (self_d)*("\033[2m"+indent_str+"\033[0m") + "\033[3;31m" + line.removeprefix(self_d*"#" + "*") + "\033[24;39m"
                                continue # to exclude quotations

                        # '#:*' -lines (quotation itself)
                        elif re.search("^" + (self_d)*"#" + "\*\:" + "[^#\:\*]+.*$", line):
                                f_line = (self_d+1)*("\033[2m"+indent_str+"\033[0m") + line.removeprefix(self_d*"#" + "*:")
                                continue # to exclude quotations
                        
                        # if line is a header, reset linenum
                        elif re.search("^===", line):
                                f_line = line
                                linenum=1

                        # if line starts with other than '#', it doesn't need to be formatted here
                        elif re.search("^[^#]*$", line):
                                f_line = line
                        
                        # if line is higher level, break and return to go back up a level
                        else:
                                lines.insert(0,line)
                                break

                        formatted_lines.append(f_line)
                                
                return formatted_lines
        
        return indent_sub_sections(lines, formatted_lines)

def __format_curly_bracketed_str(bracketed_str:str) -> str: 
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
                return formatted_str

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
        

        formatted_str = "\033[3;31m(" + ", ".join(sections) + ")\033[23;39m"
        return formatted_str


def format_section_content(section:Section, lang:str) -> str:
        """ Returns the text content of a section formatted into a nicer format.
        """
        section_content_rows = section.content.splitlines()
        # add section header
        section_content_rows .insert(0, "\033[1;34m" + section.title + "\033[22;39m")

        section_content_rows = __join_multiline_brackets(section_content_rows)

        formatted_lines = []
        for line in section_content_rows:
                newline = line


                # FIXME code repetition
                brackets = find_bracketed_strings(newline, "'''", "'''")
                while len(brackets) > 0:
                        target_bracket = brackets[0]

                        bracket_span = target_bracket[1]
                        bracket_start = bracket_span[0]
                        bracket_end = bracket_span[1]
                        bracketed_str = target_bracket[0]

                        replacement = "\033[1m" + bracketed_str.strip("'") + "\033[22m"
                        newline = newline[ : bracket_start] + replacement + newline[bracket_end : ]

                        brackets = find_bracketed_strings(newline, "'''", "'''")



                brackets = find_bracketed_strings(newline, "''", "''")
                while len(brackets) > 0:
                        target_bracket = brackets[0]

                        bracket_span = target_bracket[1]
                        bracket_start = bracket_span[0]
                        bracket_end = bracket_span[1]
                        bracketed_str = target_bracket[0]

                        replacement = "\033[3m" + bracketed_str.strip("'") + "\033[23m"
                        newline = newline[ : bracket_start] + replacement + newline[bracket_end : ]

                        brackets = find_bracketed_strings(newline, "''", "''")



                brackets = find_bracketed_strings(newline, "\[\[", "\]\]")
                while len(brackets) > 0:
                        target_bracket = brackets[0]

                        bracket_span = target_bracket[1]
                        bracket_start = bracket_span[0]
                        bracket_end = bracket_span[1]
                        bracketed_str = target_bracket[0]

                        replacement = "\033[35m" + bracketed_str.strip("[]") + "\033[39m"
                        newline = newline[ : bracket_start] + replacement + newline[bracket_end : ]

                        brackets = find_bracketed_strings(newline, "\[\[", "\]\]")



                brackets = find_bracketed_strings(newline, "{{", "}}")
                while len(brackets) > 0:
                        target_bracket = brackets[0]

                        bracket_span = target_bracket[1]
                        bracket_start = bracket_span[0]
                        bracket_end = bracket_span[1]
                        bracketed_str = target_bracket[0]

                        replacement = __format_curly_bracketed_str(bracketed_str)
                        newline = newline[ : bracket_start] + replacement + newline[bracket_end : ]

                        brackets = find_bracketed_strings(newline, "{{", "}}")



                formatted_lines.append(newline)
        
        # TODO strip unused tags, e.g. <code></code>

        formatted_lines = __format_indents(formatted_lines)

        return '\n'.join(formatted_lines)