import sqlite3 
import os
from datetime import datetime

import tools.config as config
from tools.wikiparser import WikiPage, Section
import tools.cfg_parsing_utils as cfg_parser

class Database():
    def __init__(self) -> 'Database':
        db_directory_path = os.path.expandvars(config.DB_DIRECTORY_PATH)
        db_file_path = db_directory_path + "/" + config.DB_FILE_NAME
        try:
            os.mkdir(db_directory_path)

        except FileExistsError:
            pass

        self.__db = sqlite3.connect(db_file_path)

        self.__db.isolation_level = None
        self.__db.execute("PRAGMA foreign_keys = ON") # currently unused
        self.__create_tables()




    def __create_tables(self) -> None:
        # TODO: add support for wiki pages and translations in addition to dictionary pages
        sql_create_pages_table = """
            CREATE TABLE Pages (
                id INTEGER PRIMARY KEY, 
                name TEXT, 
                language TEXT,
                content TEXT, 
                datetime DATETIME,
                CONSTRAINT uq_Pages UNIQUE(name, language)
            )
        """
        sql_create_searches_table ="""
            CREATE TABLE Searches (
                id INTEGER PRIMARY KEY, 
                text TEXT, 
                datetime DATETIME
            )
        """
        try:
            self.__db.execute(sql_create_pages_table)
            self.__db.execute("CREATE INDEX idx_name ON Pages (name)")
        except sqlite3.OperationalError as e:
            if "already exists" not in e.__str__():
                raise e

        try:
            self.__db.execute(sql_create_searches_table)
        except sqlite3.OperationalError as e:
            if "already exists" not in e.__str__():
                raise e




    def save_search(self, search:str, action:str, lang:str) -> None:
        """Save a search to local database.

        If DB_SAVE_SEARCHES is set to False in config, search is not saved.
        """
        if config.DB_SAVE_SEARCHES == False:
            return None

        self.__db.execute("INSERT INTO Searches (text, datetime) VALUES (?, DATETIME('now', 'localtime'))", [search])

    def save_page(self, page:WikiPage) -> None:
        """Save a wikipage to local database.

        If DB_SAVE_PAGES is set to False in config, page is not saved.
        """
        if config.DB_SAVE_PAGES == False:
            return None

        try:
            self.__db.execute("INSERT INTO Pages (name, language, content, datetime) VALUES (?, ?, ?, DATETIME('now', 'localtime'))", [page.title, page.language, page.text])

        except sqlite3.IntegrityError: # update page if it's already saved
            self.__db.execute("UPDATE Pages SET content = ?, datetime = DATETIME('now', 'localtime') WHERE name = ?", [page.text, page.title])




    def load_page(self, page_name:str, page_language:str) -> WikiPage | None:
        """Load a wikipage from local database.

        Returns None if:
        - the requested page doesn't exist in database 
        - the requested page's addition datetime exceeds the DB_PAGE_EXPIRATION_TIME defined in config 
        - DB_USE_SAVED_PAGES is set to False in config

        Page name matching is case sensitive.
        """
        if config.DB_USE_SAVED_PAGES == False:
            return None

        sql_get_page = """
            SELECT 
                P.name, P.content, P.language, P.datetime 
            FROM 
                Pages P 
            WHERE 
                P.name = ? AND P.language = ?
        """
        page = self.__db.execute(sql_get_page, [page_name, page_language]).fetchone()
        if page == None:
            return None

        title, text, language, date = page[0], page[1], page[2], datetime.fromisoformat(page[3])

        if  self.page_needs_update(date):
            return None
        else:
            return WikiPage(text, title, language)
    



    def get_saved_pages(self, limit:int=None) -> list[tuple]:
        """Get saved pages from local database.

        limit: maximum number of pages to fetch. If no limit given, returns all pages.

        returns a list  of tuples containing the page's id, name and datetime (of when the page was added to db). The list is in the same order in which the pages' first versions were added to db.
        returns None if no pages found.

        Pages are returned even if DB_SAVE_PAGES is set to False in config. 
        To delete saved pages, use clear_pages().
        """
        if limit == None:
            pages = self.__db.execute("SELECT P.id, P.name, P.datetime FROM Pages P ORDER BY P.id ASC").fetchall()
        elif limit <= 0:
            raise ValueError
        else:
            pages = self.__db.execute("SELECT P.id, S.name FROM Pages P ORDER BY P.id DESC LIMIT ?", [limit]).fetchall()

        if pages == None:
            return None

        return pages

    def get_saved_searches(self, limit:int=None) -> list[tuple]:
        """Get saved searches from local database.

        limit: maximum number of searches to fetch. If no limit given, returns all searches.

        returns a list of tuples with id, text and datetime in ascending order (from oldest to newest).
        returns None if no searches found.

        Searches are returned even if DB_SAVE_SEARCHES is set to False in config. 
        To delete saved searches, use clear_searches().
        """

        if limit == None:
            searches = self.__db.execute("SELECT S.id, S.text, S.datetime FROM Searches S ORDER BY S.id ASC").fetchall()
        elif limit <= 0:
            raise ValueError
        else:
            searches = self.__db.execute("SELECT S.id, S.text, S.datetime FROM Searches S ORDER BY S.id DESC LIMIT ?", [limit]).fetchall()

        if searches == None:
            return None

        return searches




    def clear_searches(self) -> None:
        """ Remove all searches from database.
        """
        self.__db.execute("DELETE FROM Searches")
        return

    def remove_search(self,target) -> None:...

    def clear_saved_pages(self) -> None: 
        """ Remove all pages from database.
        """
        self.__db.execute("DELETE FROM Searches")
        return

    def remove_saved_page(self,target) -> None:...




    def page_needs_update(self, date:datetime) -> bool:
        expiration_time = cfg_parser.expiration_time_to_seconds(config.DB_PAGE_EXPIRATION_TIME)
        cur_page_archival_time = (datetime.now() - date).seconds

        if cur_page_archival_time > expiration_time:
            return True
        else:
            return False