import requests
import tools.languages as languages
import json
import re

class WikiApi:
    def __init__(self, language:str, site:str):
        """Create WikiApi object.

        Site needs to be either "wiktionary" or "wikipedia"
        Language is the abbreviated name of wanted language e.g. "en" (English)
        """

        self.__valid_wiki_sites = ["wiktionary", "wikipedia"]
        if site not in self.__valid_wiki_sites:
            raise ValueError
        self.__site = site

        if language not in languages.supported:
            raise ValueError
        self.__language = language

        self.__url = self.__form_url(self.__language, self.__site)

        self.__cookies = []

    def __form_url(self, language:str, site:str):
        url = f"https://{language}.{site}.org/w/api.php?format=json&action=parse"
        return url

    def search(self, search_word:str) -> list:
        """Does a search on wiki and returns the results.
        """
        search_url = self.__url + search_word
        requests.get(self.__url)

    def get_page(self, page_name:str) -> tuple:
        """Get a wiki page's title, id and text content by page name.

        If page is found, returns a tuple with title, pageid and wikitext.
        If an error occurs, returns None, error code and error info.
        """
        url = self.__url + "&page=" + page_name + "&prop=wikitext"
        req = requests.get(url)
        try:
            resp_json = json.loads(req.text)["parse"]

            title = resp_json["title"]
            pageid = resp_json["pageid"]
            wikitext = resp_json["wikitext"]["*"]
            return (title, pageid, wikitext)

        except KeyError:
            resp_json = json.loads(req.text)["error"]
            error_code = resp_json["code"]
            error_info = resp_json["info"]
            return (None, error_code, error_info)


        
