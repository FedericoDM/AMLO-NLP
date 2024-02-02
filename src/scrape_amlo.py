# BOT PARA OBTENER LA VERSIÓN ESTENOGRÁFICA DE LAS MAÑANERAS DE AMLO
# Autor: Federico Domínguez Molina

# PAQUETES

import re
import pytz
import logging
import requests
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


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
        Con una fecha dada, obtiene el url de la conferencia de dicho día.
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

    @staticmethod
    def get_conference_id(todays_conference):
        """
        Obtiene el ID de la conferencia
        """
        digits = re.findall(r"\d+", todays_conference)
        conference_id = "".join(digits)
        return conference_id

    def get_conferences_links(self):
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

    def get_conferences_dates(self):
        """
        Uses RegEx to get the dates of the conferences
        """
        dates = []
        for url in self.all_urls:
            date = re.findall(r"\d{4}/\d{2}/\d{2}", url)
            dates.append(date)
        return dates

    def lambda_handler(self):

        # Sacar URL de la conferencia de hoy
        raw_links = self.get_raw_links(url)
        conference_links = self.get_conference_links(raw_links)
        today = datetime.now(pytz.timezone("America/Mexico_city"))
        today = today.strftime("%Y/%m/%d")
        todays_conference = get_conference(conference_links, today)

        if not isinstance(todays_conference, str):
            logger.info(f"No data for {today} yet...")
            return ()

        # Sacar URL de la conferencia de hoy
        clean_text, final_title = get_conference_text(todays_conference, today)
        logger.info(f"Parsed conference text for {today}")

        # Limpiar título
        final_title = final_title.replace(
            "Versión estenográfica de la conferencia", "Conferencia"
        )

        # Crear diccionario en formato de ElasticSearch
        amlo_json = {
            "title": final_title,
            "description": f"Conferencia de prensa matutina, {today}",
            "publication_date": today.replace("/", "-"),
            "url": todays_conference,
            "es_id": conference_id,
        }
