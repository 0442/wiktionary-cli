import requests
import json
import re

import tools.languages as languages
import tools.config as config

class WikiApi:
    def __init__(self, language: str, site: str):
        """Create WikiApi object.

        Site needs to be either "wiktionary" or "wikipedia"
        Language is the abbreviated name of wanted language e.g. "en" (English)
        """

        self.__valid_wiki_sites = ["wiktionary", "wikipedia"]

        if site not in self.__valid_wiki_sites:
            raise ValueError(f'unknown site "{site}"')
        self.__site = site

        if language not in languages.supported:
            raise ValueError(f'unsupported language "{language}"')
        self.__language = language

        self.__base_url = self.__form_base_url(self.__language, self.__site)

        self.__cookies = []

    def __form_base_url(self, language: str, site: str):
        url = f"https://{language}.{site}.org/w/api.php?format=json"
        return url

    def search(self, search_word: str) -> list:
        """Does a search on wiki and returns the results in a list.

        Returns None if no results found.
        """
        result_limit = config.WIKI_SEARCH_RESULTS_LIMIT
        if not 1 <= result_limit <= 500:
            raise ValueError("WIKI_SEARCH_RESULTS_LIMIT must be between 1 and 500.")

        search_url = self.__base_url + "&action=opensearch" + "&search=" + search_word + "&limit=" + str(result_limit) + "&profile=fuzzy"
        req = requests.get(search_url)
        result_json = json.loads(req.text)
        search_results = result_json[1]
        if len(search_results) == 0:
            return None
        else:
            return search_results


    def get_page(self, page_name: str) -> tuple:
        """Get a wiki page's title, id and text content by page name.

        If page is found, returns a tuple with title, pageid and wikitext.
        If an error occurs, returns None, error code and error info.
        """
        url = self.__base_url + "&action=parse" + "&page=" + page_name + "&prop=wikitext"
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



