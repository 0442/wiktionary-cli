import re

class _Section:
        def __init__(self, title:str, children:list['_Section'], depth:int, content:str="") -> None:
                self.__title = title
                self.__children = children
                self.__depth = depth
                self.__content = content
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
        
        def __str__(self):
                string = (self.depth - 1) * "|  " + self.__title
                for child in self.__children:
                        child.__str__()
                        string += '\n' + (child.depth-1)*"|  " + child.title
                return string
        

class Parser:
        # Recursively arranges a list of wiki titles into a parent-children tree.
        def __get_children(self, titles: list[str]) -> _Section:
                current_section = _Section(
                        title = titles[0].strip(" =}{"), 
                        children = [],
                        depth = int(titles[0].count("=") / 2)
                )

                if len(titles) > 1:
                        for title_index in range(1, len(titles)):
                                section_title = titles[title_index]

                                section_depth = int(section_title.count("=") / 2)

                                if section_depth > current_section.depth:
                                        current_section.add_child( self.__get_children(titles[title_index:]) )
                                else:
                                        break
                        
                return current_section



        def split_sections(self, page_text:str, page_title:str) -> _Section:
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
                sections = {}
                for s_i in range(0, len(section_spans)):
                        start = section_spans[s_i][1]
                        h = headers[s_i]

                        # if at last title, where no next title to stop at:
                        if s_i + 1 >= len(section_spans):
                                sections[h] = page_text[start :]

                        # otherwise use the next title's beginning as stop:
                        else:
                                end = section_spans[s_i + 1][0]
                                sections[h] = page_text[start : end]


                # Arrange titles into a parent-child tree
                page = self.__get_children(titles=headers)

                return page 