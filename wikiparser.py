#!/bin/env python3

import re
from pwiki.wiki import Wiki

class _Section:
        def __init__(self, title:str, content:str, children:list=[]) -> None:
                self.__children = children
                self.__content = content
                self.__depth = int(title.count("=") / 2)
                self.__title = title.strip(" =}{")

        @property
        def title(self) -> str:
                return self.__title
        @property
        def children(self) -> list['_Section']:
                return self.__children
        @property
        def depth(self) -> int:
                return self.__depth
        @property
        def content(self) -> str:
                return self.__content
        
        def add_child(self, child:'_Section') -> None:
                self.__children.append(child)
        
        def count_children(self):
                count = len(self.__children)
                for child in self.__children:
                        count += child.count_children()
                return count

        def __str__(self):
                string = (self.depth - 1) * "|  " + self.__title + '\n'
                for child in self.__children:
                        string += child.__str__()

                return string
        

class Parser:
        def __get_children(self, section_tuples:list) -> _Section:
                """
                Recursively arrange a dictionary of wiki titles and their contents into a parent-children tree.
                
                Sections is a list of tuples which contain the section title and the text content assosiated with that title.
                eg.
                sections[0] = ("title","text")
                """
                top_section = _Section(section_tuples[0][0],section_tuples[0][1],[])
                section_tuples.pop(0)

                i = 0
                while i < len(section_tuples):
                        section_title = section_tuples[i][0]
                        section_depth = int(section_title.count("=") / 2)

                        # check if section is direct child of top_section
                        # if it is, don't increment i, as a section would be skipped.
                        if section_depth == top_section.depth + 1:
                                child = self.__get_children(section_tuples) 
                                top_section.add_child(child)
                                continue
                        
                        i += 1


                return top_section




        def parse_page(self, page_text:str, page_title:str) -> _Section:
                # Note: using 'title' and 'header' synonymously in comments ie. Referring to the same thing with both words.

                header_matches = list( 
                        re.finditer("^=+" + "[^=.]+" + "=+$", page_text, re.MULTILINE)
                )

                # get the starting and ending positions for each title
                section_spans = [(0,0)]         # Pages from wiktionary api don't contain the page's main header. Pages don't often start with a subtitle, but rather with some info right under the main header. 
                                                # To not have it discarded, add title at 0. Main title needs to be added manually, otherwise this would lead to an empty section.
                for m in header_matches:
                        section_spans.append(m.span())


                # Get title names.
                # Note:
                # Number of '=' signs in title indicates the 'depth' of the title, 
                # ie. how many parent titles it has (including itself), 
                # eg. "==Translations==" has depth 2, meaning its a subtitle of the outer most title, the main title, which has depth 1.
                headers = ["=" + page_title + "="]  # name for the main header 
                for s in section_spans:
                        header = page_text[s[0] : s[1]]
                        if header != '':
                                headers.append(header)
                
                # Section contents
                sections = []
                for s_i in range(0, len(section_spans)):
                        start = section_spans[s_i][1]
                        section_title = headers[s_i]

                        # if at last title, where no next title to stop at:
                        if s_i + 1 >= len(section_spans):
                                section_content = page_text[start :]

                        # otherwise use the next title's beginning as stop:
                        else:
                                end = section_spans[s_i + 1][0]
                                section_content = page_text[start : end]
                        
                        sections.append( (section_title, section_content) )

                # Arrange titles into a parent-child tree
                page = self.__get_children(sections)

                return page 

if __name__ == "__main__":
        wiki = Wiki("fi.wiktionary.org")
        parser = Parser()

        page_title = "ämpäri"
        page = parser.parse_page(wiki.page_text(page_title),page_title)
        print(page)