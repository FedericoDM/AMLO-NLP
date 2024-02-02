# BOT PARA OBTENER LA VERSIÓN ESTENOGRÁFICA DE LAS MAÑANERAS DE AMLO
# Autor: Federico Domínguez Molina

# PAQUETES

import re
import logging
import requests
import numpy as np
from bs4 import BeautifulSoup


# CONFIGURAR LOGGER
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# PARÁMETROS
URL = "https://lopezobrador.org.mx/secciones/version-estenografica/"

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "authority": "lopezobrador.org.mx",
    "Referer": "https://www.google.com/",
    "sec-ch-ua": '''"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"''',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "Upgrade-Insecure-Requests": "1",
}


class AMLOScraper:
    """
    Class to scrape AMLO's morning conferences
    """

    URL = URL
    # Strings to filter the URLs
    STRING_1 = "version-estenografica-de"
    STRING_2 = "conferencia-de-prensa"

    # Checked this by hand
    TOTAL_PAGES = 143

    def __init__(self, headers):
        self.headers = headers

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
        r = requests.get(url, headers=headers)
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
            print(conference_link)
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
        r = requests.get(todays_conference, headers=headers)
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
        num_page = 1
        total = self.TOTAL_PAGES
        while num_page <= total:
            if num_page == 1:
                final_url = self.URL
            else:
                final_url = self.URL + f"/page/{num_page}"

            raw_links = self.get_raw_links(final_url)
            conference_links = self.get_conference_links(raw_links)
            self.all_urls.extend(conference_links)
            print(f"Done with page {num_page}")

            num_page += 1

        dates = []
        conference_ids = []
        for url in self.all_urls:
            date = re.findall(r"/\d+/\d+/\d+", url)[0]
            date = date[1:]
            digits = re.findall(r"\d+", url)
            conference_id = "".join(digits)
            conference_ids.append(conference_id)
            dates.append(date)

        self.conferences_df = pd.DataFrame(
            {"conference_id": conference_ids, "date": dates, "url": self.all_urls}
        )

        return self.conferences_df


# MAIN PIPELINE
if __name__ == "__main__":
    scraper = AMLOScraper(headers)
    conferences_df = scraper.get_conferences_df()
    conferences_df.to_csv("conferences_data.csv", index=False)
    print("Done!")
