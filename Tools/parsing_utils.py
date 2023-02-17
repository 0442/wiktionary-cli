import re
from .wikiparser import Section

# some utility functions

def __find_brackets(line:str, starting_bracket:str, ending_bracket:str) -> list[dict]:
        """
        Find brackets and their positions in a string.
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

def __get_matching_bracket_spans(brackets:list[dict]) -> list[tuple]:
        # recursive function for finding brackets (including nested ones)
        """
        Returns a list of spans of matching brackets from the output of find_brackets().
        """

        bracket_pairs = []
        if len(brackets) < 1:
                return bracket_pairs

        prev_brack = brackets.pop(0)

        while len(brackets) > 0:
                # if opening bracket
                if brackets[0]["string"] == "{{" and prev_brack["string"] == "}}":
                        prev_brack = brackets.pop(0)
                        continue

                # if opening, nested bracket, recurse
                if brackets[0]["string"] == "{{" and prev_brack["string"] == "{{":
                        #prev_brack = brackets.pop(0)
                        nest_bracks = __get_matching_bracket_spans(brackets)
                        [bracket_pairs.append(b) for b in nest_bracks]
                        continue

                # if closing brackets, add to matching pairs
                if brackets[0]["string"] == "}}" and prev_brack["string"] == "{{":
                        bracket_pairs.append( (prev_brack["start"], brackets[0]["end"]) )
                        prev_brack = brackets.pop(0)
                        continue
                
                if brackets[0]["string"] == "}}" and prev_brack["string"] == "}}":
                        break

        return bracket_pairs

def find_bracketed_strings(string:str, starting_bracket:str, ending_bracket:str) -> tuple:
        """ 
        Wraps 'find_brackets' and 'get_matching_bracket_spans' 
        for finding all bracketed strings and their spans, 
        including nested ones, in a string.
        """
        brackets = __find_brackets(string, starting_bracket, ending_bracket)
        br_spans = __get_matching_bracket_spans(brackets)
        bracketed_strs = []
        for span in br_spans:
                bracketed_strs.append( (string[span[0] : span[1]], span) )

        return bracketed_strs


def __format_indents(lines:list, self_d:int=1) -> list:
        """Returns lines of a wiki page with indentation and line numbers added.

        Recursively finds lines to be indented and numbered.
        """
        indent_str = "▏   "
        formatted_lines = []
        linenum = 1
        while len(lines) > 0:
                line = lines[0].strip()

                # '##' -lines, ie. if sub, go down a level, recurse
                if re.search("^" + (self_d+1)*"#" + "[^#\:\*]+.*$", line):
                        subs = __format_indents(lines, self_d + 1)
                        for s in subs:
                                formatted_lines.append(s)

                # '#' -lines, ie. if on same level 
                elif re.search("^" + (self_d)*"#" + "[^#\:\*]+.*$", line):
                        f_line = (self_d-1)*("\033[2m" + indent_str + "\033[0m") + str(linenum) + "." + line.removeprefix(self_d*"#")
                        lines.pop(0)
                        formatted_lines.append(f_line)
                        linenum += 1

                # '#:' -lines / examples?
                elif re.search("^" + (self_d)*"#" + "\:" + "[^#\:\*]+.*$", line):
                        f_line = (self_d)*("\033[2m"+indent_str+"\033[0m") + "\033[31m" + line.removeprefix(self_d*"#" + ":") + "\033[39m"
                        lines.pop(0)
                        formatted_lines.append(f_line)

                # '#*' -lines / quotes?
                elif re.search("^" + (self_d)*"#" + "\*" + "[^#\:\*]+.*$", line):
                        f_line = (self_d)*("\033[2m"+indent_str+"\033[0m") + "\033[3;31m" + line.removeprefix(self_d*"#" + "*") + "\033[24;39m"
                        lines.pop(0)
                        formatted_lines.append(f_line)

                # '#:*' -lines
                elif re.search("^" + (self_d)*"#" + "\*\:" + "[^#\:\*]+.*$", line):
                        f_line = (self_d+1)*("\033[2m"+indent_str+"\033[0m") + line.removeprefix(self_d*"#" + "*:")
                        lines.pop(0)
                        formatted_lines.append(f_line)
                
                # if line is a header, reset linenum
                elif re.search("^===", line):
                        linenum=1
                        lines.pop(0)
                        formatted_lines.append(line)

                # if line starts with other than '#', it doesn't need to be formatted here
                elif re.search("^[^#]*$", line):
                        lines.pop(0)
                        formatted_lines.append(line)
                
                # if line is higher level, break and return to go back up a level
                else:
                        break

        return formatted_lines

def __format_curly_bracketed_str(bracketed_str:str) -> str: 
        sections = bracketed_str.strip("}{").split("|")

        # format quotes
        if "quote-book" in sections or "quote-journal" in sections or "quote-web" in sections or "quote-text" in sections:
                """
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
                """
                return "" # exclude quotes, as they take up a lot of space

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
        """ Returns the text of a section formatted into a nicer format.
        """
        parsed_lines = section.content.splitlines()
        # add section header
        parsed_lines.insert(0, "\033[1;34m" + section.title + "\033[22;39m")

        # format '''abc'''
        # bold words surrounded by triple " ' "
        line_i = 0
        for line in parsed_lines:
                newline = ""
                curls = re.findall("\'{3}" + "[^']+" + "\'{3}", line)
                for c in curls:
                        new = c.strip("'")
                        new = "\033[1m" + new + "\033[22m"

                        newline = line.replace(c,new)
                        parsed_lines[line_i] = newline
                line_i += 1


        # format '[[abcd]]'
        # doesn't handle nested square brackets. 
        format_squares = []
        for line in parsed_lines:
                newline = ""
                for word in re.split("(\ |\.|\,|\;)", line):
                        # find the beginning of [[]]
                        if word.find("[[") != -1:
                                word = "\033[35m" + word.replace("[", "")
                        # find the end of [[]]
                        if word.find("]]") != -1:
                                word = word.replace("]", "") + "\033[39m"

                        newline += word

                format_squares.append(newline)


        # TODO: use this method for other brackets and '''abc''' aswell
        format_curly_brackets = []
        for line in format_squares:
                newline = line

                brackets = find_bracketed_strings(line, "{{", "}}")
                while len(brackets) > 0:
                        target_bracket = brackets[0]

                        bracket_span = target_bracket[1]
                        bracket_start = bracket_span[0]
                        bracket_end = bracket_span[1]
                        bracketed_str = target_bracket[0]

                        replacement = __format_curly_bracketed_str(bracketed_str)
                        newline = newline[ : bracket_start] + replacement + newline[bracket_end: ]

                        brackets = find_bracketed_strings(newline, "{{", "}}")

                format_curly_brackets.append(newline)
        
        # TODO: strip unused tags, e.g. <code></code>

        ## FORMAT LINES
        indented_lines = []
        indented_lines = __format_indents(format_curly_brackets)

        return '\n'.join(indented_lines)