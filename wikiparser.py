#!/bin/env python3

import re

word_classes = {
        "en" : [
                "Adjective", "Adverb", "Article", "Conjuction", "Noun", "Numeral", 
                "Adposition", "Preposition", "Postposition", 
                "Participle", "Pronoun", "Verb"
        ],
        "fi" : ["Adjektiivi", "Adverbi", "Artikkeli", "Konjunktio", "Substantiivi", "Numeraali", 
                "Adpositio", "Prepositio", "Postpositio", 
                "Partisiippi", "Pronomini", "Verbi"
        ],
        "sv" : [""],
}

class Section:
        def __init__(self, title:str, content:str, children:list=[]) -> None:
                self.__children = children
                self.__content = content
                self.__depth = int(title.count("=") / 2)
                self.__title = title.replace("=","").replace("}","").replace("{","")

        @property
        def title(self) -> str:
                return self.__title
        @property
        def children(self) -> list['Section']:
                return self.__children
        @property
        def depth(self) -> int:
                return self.__depth
        @property
        def content(self) -> str:
                return self.__content
        
        @children.setter
        def children(self, children):
                self.__children =  children

        
        def add_child(self, child:'Section') -> None:
                self.__children.append(child)
        
        def count_children(self):
                """
                Recursively count section's all child sections. (excluding itself)
                """
                count = len(self.__children)
                for child in self.__children:
                        count += child.count_children()
                return count

        def __get_sections(self, section_title:str) -> list['Section']:
                """
                Return all sections with the given title.
                """
                matches = []
                if self.title == section_title: 
                        matches.append(self)

                for c in self.children:
                        c_matches = c.__get_sections(section_title)
                        if len(c_matches) != 0:
                                for i in c_matches:
                                        matches.append(i)

                return matches

        def find(self, sect_path:str) -> 'Section':
                """
                Return the first occurence of a section with the given title.\n
                Return None if no section found. 
                Either a section name can be given or a path, eg. English/Noun
                """
                # format path
                path = sect_path.split("/")
                path = [s.strip(" /") for s in path if s]
                
                # find the wanted section
                sect = self
                for s in path:
                        matches = sect.__get_sections(s)
                        if len(matches) == 0:
                                return None
                        else:
                                sect = matches[0]

                return sect

        def find_all(self, section_title:str) -> list['Section']:
                """
                Return all sections with the given title.
                """
                matches = self.__get_sections(section_title)
                return matches

        def __str__(self):
                string = (self.depth - 1) * "\033[2m▏  \033[0m" + self.__title
                for child in self.__children:
                        string += '\n' + child.__str__()

                return string
        

class WikiParser:
        def __init__(self, page_text:str, page_title:str) -> None:
                self.__page_text = page_text
                self.__page_title = page_title
                self.__page = self.__parse_page()

        def __get_children(self, section_tuples:list, child_depth:int=1) -> Section:
                """
                Recursively arrange a dictionary of wiki titles and their contents into a parent-child tree.
                
                Sections is a list of tuples which contain the section title and the text content assosiated with that title.
                eg.
                sections[0] = ("title","text")
                """

                children = []
                i = 0
                while i < len(section_tuples):
                        sect_title = section_tuples[i][0]
                        sect_depth = int(sect_title.count("=") / 2)
                        if sect_depth == child_depth:
                                child_sect = Section(sect_title, section_tuples[i][1], [])
                                section_tuples.pop(0)
                                child_children = self.__get_children(section_tuples, child_depth+1)
                                child_sect.children = child_children
                                children.append(child_sect)
                                i-=1
                        elif sect_depth == child_depth - 1:
                                break
                        i+=1

                return children


        def __parse_page(self) -> Section:
                """
                Parse wiki page into a section object for easier data extraction
                """
                # Note: using 'title' and 'title' synonymously in comments ie. Referring to the same thing with both words.

                title_matches = list( 
                        re.finditer("^=+" + "[^=]+" + "=+$", self.__page_text, re.MULTILINE)
                )

                # get the starting and ending positions for each title
                section_spans = [(0,0)]         # Pages from wiktionary api don't contain the page's main title. Pages don't often start with a subtitle, but rather with some info right under the main title. 
                                                # To not have it discarded, add title at 0. Main title needs to be added manually, otherwise this would lead to an empty section.
                for m in title_matches:
                        section_spans.append(m.span())


                # Get title names.
                # Note:
                # Number of '=' signs in title indicates the 'depth' of the title, 
                # ie. how many parent titles it has (including itself), 
                # eg. "==Translations==" has depth 2, meaning its a subtitle of the outer most title, the main title, which has depth 1.
                titles = ["=" + self.__page_title + "="]  # name for the main title 
                for s in section_spans:
                        title = self.__page_text[s[0] : s[1]]
                        if title != '':
                                titles.append(title)
                
                # Section contents
                sections = []
                for s_i in range(0, len(section_spans)):
                        start = section_spans[s_i][1]
                        section_title = titles[s_i].strip()

                        # if at last title, where no next title to stop at:
                        if s_i + 1 >= len(section_spans):
                                section_content = self.__page_text[start :]

                        # otherwise use the next title's beginning as stop:
                        else:
                                end = section_spans[s_i + 1][0]
                                section_content = self.__page_text[start : end]
                        
                        sections.append( (section_title, section_content) )

                # Arrange titles into a parent-child tree
                page = self.__get_children(sections)

                return page[0]
        
        def format_section_content(self, section_name:str, lang:str) -> str:
                """
                
                """
                indent_str = "▏   "
                # Recursive function for indents and line nums
                def sub_defs(lines:list, self_d:int=1):
                        formatted_lines = []
                        linenum = 1
                        while len(lines) > 0:
                                line = lines[0].strip()

                                # '##' -lines, ie. if sub, go down a level, recurse
                                if re.search("^" + (self_d+1)*"#" + "[^#\:\*]+.*$", line):
                                        subs = sub_defs(lines, self_d + 1)
                                        for s in subs:
                                                formatted_lines.append(s)

                                # '#' -lines, ie. if on same level 
                                elif re.search("^" + (self_d)*"#" + "[^#\:\*]+.*$", line):
                                        f_line = (self_d-1)*("\033[2m" + indent_str + "\033[0m") + str(linenum) + "." + line.removeprefix(self_d*"#")
                                        lines.pop(0)
                                        formatted_lines.append(f_line)
                                        linenum += 1

                                # '#:' -lines
                                elif re.search("^" + (self_d)*"#" + "\:" + "[^#\:\*]+.*$", line):
                                        f_line = (self_d)*("\033[2m"+indent_str+"\033[0m") + line.removeprefix(self_d*"#" + ":")
                                        lines.pop(0)
                                        formatted_lines.append(f_line)

                                # '#*' -lines
                                elif re.search("^" + (self_d)*"#" + "\*" + "[^#\:\*]+.*$", line):
                                        f_line = (self_d)*("\033[2m"+indent_str+"\033[0m") + line.removeprefix(self_d*"#" + "*")
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



                section = self.page.find(section_name)
                if not section:
                        return None
                parsed_lines = section.content.splitlines()
                # add section header
                parsed_lines.insert(0, "\033[1;34m" + section.title + "\033[22;39m")

                # format '''abc'''
                # bold words surrounded by triple " ' "
                line_i = 0
                for line in parsed_lines:
                        newline = ""
                        curls = re.findall("\'{3}" + "[^'.]+" + "\'{3}", line)
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
                                if word.find("[[")!=-1:
                                        word = "\033[35m" + word.replace("[", "")
                                # find the end of [[]]
                                if word.find("]]")!=-1:
                                        word = word.replace("]", "") + "\033[39m"

                                newline += word

                        format_squares.append(newline)


                # format '{{a|b|c...}}'
                # doesn't handle nested curly brackets. 
                line_i = 0
                for line in format_squares:
                        newline = ""
                        curls = re.findall("{{" + "[^}{]+" + "}}", line)
                        for c in curls:
                                #new = c.strip("}{ ").split("|")
                                new = c[2:len(c)-2].split("|")
                                # remove first two values, eg. 'a' and 'b' from {{a|b|c...}}. They often contain something like 'en'
                                if len(new) >= 3:
                                        new.pop(0) if len(new[0]) <= 2 else 0
                                        new.pop(0) if len(new[0]) <= 2 else 0

                                new = "\033[3;31m(" + ", ".join(new) + ")\033[23;39m"

                                newline = line.replace(c,new)
                                format_squares[line_i] = newline
                        line_i += 1
                

                indented_lines = []
                indented_lines = sub_defs(format_squares)

                return '\n'.join(indented_lines)
        
        @property
        def page(self) -> Section:
                return self.__page


if __name__ == "__main__":
        import sys
        from pwiki.wiki import Wiki
        exit(1) if len(sys.argv) < 2 else None
        wiki = Wiki("en.wikipedia.org")
        pt = wiki.page_text(sys.argv[1])  
        parser = WikiParser(pt, sys.argv[1])
        print("en.wikpedia.org\n", parser.format_section_content(sys.argv[1], "en"))
        exit(0)
