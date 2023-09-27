import os
import json
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from logger import Logger

class Scrapper:
    def __init__(self, max_page: int):
        self.host = "https://yts.rs"
        self.soup = None
        self.max_page = max_page
        self.links = []
        self.magnets = []
        self.torrents = []
        self.downloaded = 0
        self.logger = Logger()

        self.__launch__()

    def __load_links__(self):
        if (os.path.exists("links.json") == True):
            with open("links.json", 'r') as f:
                self.links = json.loads(f.read())
        if (os.path.exists("torrents") == True):
            self.downloaded = len(os.listdir("torrents")) - 1
            self.links = self.links[self.downloaded:]

    def __launch__(self):
        self.__load_links__()
        if (len(self.links) == 0):
            for i in tqdm(range(0, self.max_page), ascii = True, bar_format="{percentage:3.0f}%|{bar:50}{r_bar}", leave = False):
                self.__get_page_links__(i + 1)
            self.__save__(self.links, "links.json")
        self.__get_torrents__()

    def __get_page_links__(self, index: int):
        tags = []
        r = self.__invoke__(
            "get",
            f"{self.host}/browse-movies",
            [
                ("page", index)
            ],
            {},
            {}
        )

        if (r.status_code == 200):
            self.soup = BeautifulSoup(r.text, 'html.parser')
            tags = self.soup.find_all("a", class_="text--bold palewhite title")

            for tag in tags:
                self.links.append(tag.get("href"))

    def __get_torrents__(self):
        tags = []
        r = None
        href = None
        title = None
        resolutions = " 1080p Torrent"
        clean_title = None
        payload = {}
        folder = None
        purge = 0

        for link in tqdm(self.links, ascii = True, bar_format="{percentage:3.0f}%|{bar:50}{r_bar}", leave = True):
            r = self.__invoke__(
                "get",
                f"{self.host}{link}",
                [],
                {},
                {}
            )

            if (r.status_code == 200):
                self.soup = BeautifulSoup(r.text, 'html.parser')
                tags = self.soup.find_all("a", class_="download-torrent popup123")

                for tag in tags:
                    href = tag.get("href")
                    title = tag.get("title")[9:]
                    payload = {
                        "title": title,
                        "link": href
                    }
                    if (resolutions in title):
                        clean_title = title.replace(resolutions, '')
                        if ("magnet:?xt=urn:btih:" not in href ):
                            payload["title"] = clean_title.lower()
                            if (self.__validate_torrent__(payload) == True):
                                self.torrents.append(payload)
            self.__purge__(purge)
            purge += 1

    def __purge__(self, index: int):
        self.__download_torrents__()
        #self.__save__(self.torrents, f"catalog/{index}.json")
        self.torrents.clear()

    def __download_torrents__(self):
        for torrent in tqdm(self.torrents, ascii = True, bar_format="{percentage:3.0f}%|{bar:50}{r_bar}", leave = False):
            r = requests.get(torrent["link"])
            with open("torrents/{}.torrent".format(self.__clean__(torrent["title"])), "wb") as f:
                f.write(r.content)

    def __clean__(self, name: str):
        clean = []

        for letter in name:
            if (letter.isalnum() == True or letter == ' '):
                clean.append(letter)
        return ("".join(clean))

    def __validate_torrent__(self, payload):
        for torrent in self.torrents:
            if (torrent["title"] == payload["title"]):
                return (False)
        return (True)

    def __validate_magnet__(self, payload):
        for magnet in self.magnets:
            if (magnet["title"] == payload["title"]):
                return (False)
        return (True)

    def __save__(self, list_to_save, file_name):
        with open(file_name, "w") as f:
            json.dump(list_to_save, f, indent = 4)

    def __invoke__(self, method, url: str, params: list, headers: dict, json: dict):
        request = requests.Request(
            method,
            url = url,
            params = params,
            headers = headers,
            json = json
        )
        prepared = request.prepare()
        response = requests.Session().send(prepared)

        return (response)

if (__name__ == "__main__"):
    Scrapper(2712)
