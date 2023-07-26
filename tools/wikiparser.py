import re
import tools.languages as languages
import tools.options as options
from tools.config import PATH_SEP

class Section:
        def __init__(self, title: str, content: str, children: list=[], number:int=None) -> 'Section':
                self.__children = children
                self.__content = content
                self.__depth = int(title.count("=") / 2)
                self.__title = title.replace("=","").replace("}","").replace("{","").strip()
                self.__number = number

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
        @property
        def number(self) -> int:
                return self.__number

        @children.setter
        def children(self, children):
                self.__children =  children
        @title.setter
        def title(self, title):
                self.__title = title

        def add_child(self, child: 'Section') -> None:
                self.__children.append(child)

        def count_children(self):
                """ Recursively count section's all child sections. (meaning this section excluded)
                """
                count = len(self.__children)
                for child in self.__children:
                        count += child.count_children()
                return count

        def __all_children(self):
                """Returns a list of all direct and indirect children"""
                c = self.__children
                for dc in self.__children:
                        c += dc.__all_children()
                return c

        def __get_sections(self, section_title: str) -> list['Section']:
                """ Return all sections with the given title.
                Case insensitive.
                """
                # TODO add wildcards *
                matches = []
                if self.title.lower() == section_title.lower() or str(self.number) == section_title.lower():
                        matches.append(self)

                for c in self.children:
                        c_matches = c.__get_sections(section_title)
                        if len(c_matches) != 0:
                                for i in c_matches:
                                        matches.append(i)

                return matches

        def find(self, search: str) -> list['Section']:
                """Return sections with the given title.

                Return None if no section found.
                Either a section name can be given or a path, eg. English/Noun
                Search is case insensitive.
                """
                result = self._find_by_path(search)
                if len(result) != 0:
                        return result
                else:
                        return self._find_all(search)



        def _find_all(self, section_title: str) -> list['Section']:
                """
                Return all sections with the given title.
                """
                # TODO add wildcards *
                matches = self.__get_sections(section_title)
                return matches

        def _find_one(self, section_title: str) -> 'Section':
                """Return first section with given title
                returns None if no section found
                """
                matches = self.__get_sections(section_title)
                if len(matches) > 0:
                        return matches[0]
                else:
                        return None

        def _find_by_path(self, sect_path:str|list, _results:list['Section']=[]):
                """Return Section(s) to which sect_path points.
                If path starts with path sep, next sections are strictrly searched from this sections children.
                If path does not start with path sep, the first subsection match, which may not be a direct child of this section, is used as root.
                """
                # convert str path to list
                if sect_path.__class__ is str:
                        sect_path = sect_path.split(PATH_SEP)
                sect_path = [s.strip().lower() for s in sect_path if s]
                if options.VERBOSE: print(f'remaining path {sect_path}; at "{self.title}"; children: {[ s.title for s in self.__children]}')



                if len(sect_path) == 0:
                        return [ self ]

                next_sect_search = sect_path[0]
                next_sects = []

                for s in self.children:
                        if s.title.lower() == next_sect_search or str(s.number) == next_sect_search :
                                next_sects.append(s)
                        elif next_sect_search == "*":
                                next_sects.append(s)
                        elif next_sect_search == "**":
                                next_sects.append(s)
                                next_sects.append(self)
                                next_sects += s.__all_children()

                if len(sect_path) >= 1:
                        new_results = []
                        for s in next_sects:
                                new_results += s._find_by_path(sect_path[1:], _results)
                        _results = list(set(_results + new_results))

                return _results

        def __str__(self, _relative_depth: int=1):
                #string = (relative_depth-1) * "\033[2m▏  \033[0m" + self.__title
                string = (_relative_depth-1) * "#" + self.__title
                for child in self.__children:
                        string += '\n' + child.__str__(_relative_depth+1)

                return string


class WikiPage:
        valid_wiki_sites = [
                "wikipedia",
                "wiktionary"
        ]

        search_keywords = {
                "definitions": ["@d", "@definitions"],
                "translations": ["@t", "@translations"],
        }

        def __init__(self, page_text: str, page_title: str, language: str, site) -> 'WikiPage':
                if site not in WikiPage.valid_wiki_sites:
                        raise ValueError("Unsupported site")

                self.__text = page_text
                self.__title = page_title
                self.__language = language
                self.__root_section = self.__split_into_sections()
                self.__site = site


        def __get_children(self, section_tuples: list, child_depth: int=1, _sect_num:int=1) -> Section:
                """ Recursively arrange a dictionary of wiki titles and their contents into a parent-child tree.

                Section_tuples is a list of tuples which contain the section title and the text content assosiated with that title.
                eg.
                sections[0] = ("title","text")
                """

                children = []
                i = 0
                while i < len(section_tuples):
                        sect_title = section_tuples[i][0]
                        cur_depth = int(sect_title.count("=") / 2)

                        if cur_depth == child_depth:
                                child_sect = Section(sect_title, section_tuples[i][1], [], _sect_num)
                                section_tuples.pop(0)
                                child_children = self.__get_children(section_tuples, child_depth+1)
                                child_sect.children = child_children
                                children.append(child_sect)
                                i-=1

                        elif cur_depth == child_depth - 1:
                                break

                        _sect_num += 1
                        i+=1

                return children


        def __split_into_sections(self) -> Section:
                """ Parse wiki page's content into a section object
                """
                title_matches = list(re.finditer("^=+" + "[^=]+" + "=+$", self.__text, re.MULTILINE))

                # get the starting and ending positions for each title
                section_spans = [(0,0)]

                for m in title_matches:
                        section_spans.append(m.span())

                titles = ["=" + self.__title + "="]  # add title for page root
                for s in section_spans:
                        title = self.__text[s[0] : s[1]]
                        if title != '':
                                titles.append(title.strip())

                sections = []
                for s_i in range(0, len(section_spans)):
                        start = section_spans[s_i][1]
                        section_title = titles[s_i].strip()

                        # if at last title, where no next title to stop at:
                        if s_i + 1 >= len(section_spans):
                                section_content = self.__text[start : ]

                        # otherwise use the next title's beginning as stop:
                        else:
                                end = section_spans[s_i + 1][0]
                                section_content = self.__text[start : end].strip()

                        sections.append( (section_title, section_content) )

                # Arrange titles into a parent-child tree
                page_root_section = self.__get_children(sections)

                return page_root_section[0]

        def find_page_sections(self, search: str) -> list[Section] | None:
                """Find sections from this page.

                Returns a list of sections that match the search. If no matches are found, returns None

                Search can either be a path to a section, a section name, or a keyword that matches a group of sections, e.g. 'definitions' for wiktionary pages, which matches Noun, Verb, etc.. sections
                """

                root_section = self.__root_section

                matching_sections = []

                if search.lower() in self.search_keywords["definitions"]:
                        for wc in languages.definitions[self.__language]:
                                path_to_def = f"{languages.abbrev_table[self.__language][self.__language]}{PATH_SEP}**{PATH_SEP}{wc}"
                                results = root_section.find(path_to_def)
                                if results:
                                        matching_sections += results

                elif search.lower() in self.search_keywords["translations"]:
                        for wc in languages.definitions[self.__language]:
                                path_to_tr = f"{languages.abbrev_table[self.__language][self.__language]}{PATH_SEP}**{PATH_SEP}{wc}{PATH_SEP}{languages.translations[self.__language]}"
                                results = root_section.find(path_to_tr)
                                if results:
                                        results.title += " " + "(" + wc + ")"
                                        matching_sections += (results)

                else:
                        results = root_section.find(search)
                        if results:
                                matching_sections += results

                return matching_sections

        def __str__(self):
                def add_sect_content(sect: Section) -> str:
                        page_str = ""
                        print(len(sect.children))
                        if len(sect.children) != 0:
                                for c in sect.children:
                                        page_str += add_sect_content(c)

                        return sect.content + page_str

                return add_sect_content(self.__root_section)



        @property
        def root_section(self) -> Section:
                return self.__root_section
        @property
        def text(self) -> str:
                return self.__text
        @property
        def title(self) -> str:
                return self.__title
        @property
        def language(self) -> str:
                return self.__language
        @property
        def site(self) -> str:
                return self.__site
