"""This script scrapes AMLO's morning conferences from his official website"""

# Autor: Federico Domínguez Molina

# PAQUETES

import os
import re
import time
import logging
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

import argparse

# Local imports
URL = "https://lopezobrador.org.mx/secciones/version-estenografica/"

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "authority": "lopezobrador.org.mx",
    "Referer": "https://www.google.com/",
    "sec-ch-ua": '''"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"''',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "Upgrade-Insecure-Requests": "1",
}

DATA_PATH = "src/data/"


# CONFIGURAR LOGGER
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class AMLOScraper:
    """
    Class to scrape AMLO's morning conferences
    """

    URL = URL
    # Strings to filter the URLs
    STRING_1 = "version-estenografica-de"
    STRING_2 = "conferencia-de-prensa"
    CONFERENCES_DATA_PATH = f"{DATA_PATH}/text_files/"
    COUNT_THRESHOLD = 50

    # Checked this by hand
    TOTAL_PAGES = 144

    def __init__(self, headers):
        self.headers = headers
        self.sleep_time = 2

    def get_raw_links(self, url):
        """[Saca lista de todos los hrefs de la pagina de AMLO]

        Parameters
        ----------
        url : [str]
            [Url base donde están todos los links de las transcripciones de las conferencias]

        Returns
        -------
        raw_links: [list]
            [Lista con todos los urls de la página]
        """
        r = requests.get(url, headers=self.headers)
        raw_html = r.text
        soup = BeautifulSoup(raw_html, "html.parser")
        a_elements = soup.find_all("a", href=True)
        raw_links = []
        for a_element in a_elements:
            raw_links.append(a_element["href"])

        return raw_links

    def get_conference_links(self, raw_links):
        """[A partir de una lista, obtiene los urls que únicamente
        corresponden a las conferencias]

        Parameters
        ----------
        raw_links : [list]
            [lista con todos los urls de la página]

        Returns
        -------
        conference_links: [list]
            [lista con todos los urls de las conferencias]
        """
        conference_links = []
        for raw_link in raw_links:
            if self.STRING_1 in raw_link and self.STRING_2 in raw_link:
                conference_links.append(raw_link)
            else:
                continue
        conference_links = list(set(conference_links))
        return conference_links

    # Necesitaremos extraer la conferencia del día de hoy con base en la fecha
    def get_conference(self, conference_links, date):
        """
        Gets the url of a given conference date
        - conference_links: Links de todas las conferencias de AMLO
        - date: String con la fecha de interés
        """
        date_conference = np.nan

        for conference_link in conference_links:
            if date in conference_link:
                date_conference = conference_link
                return date_conference

        return date_conference

    def get_conference_text(self, todays_conference, date):
        """
        Obtiene el texto de la conferencia correspondiente y el título
        Recibe:
            - todays_conference: URL con la fecha de interés
            - date: string con la fecha para crear el título
        """
        r = requests.get(todays_conference, headers=self.headers)
        # Parsear HTML
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("title")
        # Sacar título y texto
        final_title = title.text + " | " + date
        raw_paragraphs = soup.find_all("p")
        clean_paragraphs = []
        for raw_paragraph in raw_paragraphs:
            clean_paragraphs.append(raw_paragraph.text.strip())
        clean_text = " ".join(clean_paragraphs)

        return clean_text, final_title

    def get_conferences_df(self):
        """
        Obtiene los links de las conferencias
        """
        self.all_urls = []
        total = self.TOTAL_PAGES
        for num_page in range(1, total + 1):
            if num_page == 1:
                final_url = self.URL
            else:
                final_url = self.URL + f"/page/{num_page}"

            try:
                raw_links = self.get_raw_links(final_url)
                conference_links = self.get_conference_links(raw_links)
                self.all_urls.extend(conference_links)
                print(f"Done with page {num_page}")

            except Exception as e:
                print(f"Error with page {num_page}")
                print(e)

            num_page += 1

        dates = []
        conference_ids = []
        for url in self.all_urls:
            date = re.findall(r"/\d+/\d+/\d+", url)[0]
            date = date[1:]
            conference_id = date.replace("/", "")
            conference_ids.append(conference_id)
            dates.append(date)

        self.conferences_df = pd.DataFrame(
            {"conference_id": conference_ids, "date": dates, "url": self.all_urls}
        )

        # Remove duplicates and sort by date
        self.conferences_df = self.conferences_df.drop_duplicates(
            subset="conference_id", keep="first"
        )
        self.conferences_df.sort_values(by="date", ascending=True, inplace=True)
        self.conferences_df = self.conferences_df.reset_index(drop=True)

        return self.conferences_df

    def get_all_conferences_text(self):
        """
        Obtiene el texto de todas las conferencias
        """
        # Check if path exists
        if not os.path.exists(self.CONFERENCES_DATA_PATH):
            print("Creating data path")
            os.makedirs(self.CONFERENCES_DATA_PATH)
        else:
            print("Data path already exists")

        counter = 1

        for index, row in self.conferences_df.iterrows():
            date = row["date"]
            url = row["url"]
            id = row["conference_id"]
            text, title = self.get_conference_text(url, date)
            with open(
                f"{self.CONFERENCES_DATA_PATH}/{id}.txt", "w", encoding="utf-8"
            ) as file:
                # Add title to the file
                file.write(title)
                file.write("\n")
                file.write(text)

            print(f"Extracted and saved text {title}")

            if counter % self.COUNT_THRESHOLD == 0:
                print(f"Done with {counter} conferences")
                time.sleep(self.sleep_time)

            counter += 1


# MAIN PIPELINE

parser = argparse.ArgumentParser(description="Get AMLO's morning conferences")

parser.add_argument(
    "mode",
    type=str,
    choices=["single conference", "all"],
    help="Mode to run the scraper",
)

parser.add_argument("--date", type=str, help="Date of the conference to scrape")

args = parser.parse_args()

if __name__ == "__main__":

    if args.mode == "single conference":

        date = args.date
        scraper = AMLOScraper(HEADERS)
        print("Getting conference for date", date)

        # Get raw links
        raw_links = scraper.get_raw_links(URL)
        conference_links = scraper.get_conference_links(raw_links)
        todays_conference = scraper.get_conference(conference_links, date)
        text, title = scraper.get_conference_text(todays_conference, date)

        id = date.replace("/", "")
        with open(f"{DATA_PATH}/{id}.txt", "w", encoding="utf-8") as file:
            file.write(title)
            file.write("\n")
            file.write(text)

        print(f"Extracted and saved text {title}")

        # Add to the dataframe
        conferences_df = pd.read_csv("conferences_data.csv")
        new_row = {"conference_id": id, "date": date, "url": todays_conference}
        conferences_df = conferences_df.append(new_row, ignore_index=True)
        conferences_df.to_csv("conferences_data.csv", index=False)

        print("Done!")

    else:

        scraper = AMLOScraper(HEADERS)
        print("Getting conferences data")
        conferences_df = scraper.get_conferences_df()
        conferences_df.to_csv("conferences_data.csv", index=False)
        print("Done!")
        scraper.get_all_conferences_text()
