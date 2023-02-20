import re

class Section:
        def __init__(self, title:str, content:str, children:list=[]) -> 'Section':
                self.__children = children
                self.__content = content
                self.__depth = int(title.count("=") / 2)
                self.__title = title.replace("=","").replace("}","").replace("{","").strip()

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
                """ Recursively count section's all child sections. (meaning this section excluded)
                """
                count = len(self.__children)
                for child in self.__children:
                        count += child.count_children()
                return count

        def __get_sections(self, section_title:str) -> list['Section']:
                """ Return all sections with the given title.
                Case insensitive.
                """
                # TODO add wildcards * 
                matches = []
                if self.title.lower() == section_title.lower(): 
                        matches.append(self)

                for c in self.children:
                        c_matches = c.__get_sections(section_title)
                        if len(c_matches) != 0:
                                for i in c_matches:
                                        matches.append(i)

                return matches

        def find(self, sect_path:str) -> 'Section':
                """Return the first occurence of a section with the given title.

                Return None if no section found. 
                Either a section name can be given or a path, eg. English/Noun
                Search is case insensitive.
                """
                # format path
                path = sect_path.split("/")
                path = [s.strip(" /").lower() for s in path if s]
                
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
                # TODO add wildcards * 
                matches = self.__get_sections(section_title)
                return matches

        def __str__(self, relative_depth:int=1):
                #string = (self.depth - 1) * "\033[2m▏  \033[0m" + self.__title
                string = (relative_depth-1) * "\033[2m▏  \033[0m" + self.__title
                for child in self.__children:
                        string += '\n' + child.__str__(relative_depth=relative_depth+1)

                return string
        

class WikiParser:
        def __init__(self, page_text:str, page_title:str) -> 'WikiParser':
                self.__page_text = page_text
                self.__page_title = page_title
                self.__page_root_section = self.__split_into_sections()

        def __get_children(self, section_tuples:list, child_depth:int=1) -> Section:
                """ Recursively arrange a dictionary of wiki titles and their contents into a parent-child tree.
                
                Section_tuples is a list of tuples which contain the section title and the text content assosiated with that title.
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


        def __split_into_sections(self) -> Section:
                """ Parse wiki page into a section object
                """
                # Note: using 'title' and 'title' synonymously in comments ie. Referring to the same thing with both words.

                title_matches = list(re.finditer("^=+" + "[^=]+" + "=+$", self.__page_text, re.MULTILINE))

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
                                titles.append(title.strip())
                
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
                                section_content = self.__page_text[start : end].strip()
                        
                        sections.append( (section_title, section_content) )

                # Arrange titles into a parent-child tree
                page_root_section = self.__get_children(sections)

                return page_root_section[0]
        
        
        @property
        def page_root_section(self) -> Section:
                return self.__page_root_section
        @property
        def page_text(self) -> str:
                return self.__page_text
        @property
        def page_title(self) -> str:
                return self.__page_title
