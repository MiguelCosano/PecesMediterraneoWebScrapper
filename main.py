from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
import logging
from typing import Optional
import pandas as pd

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

URL = "https://pecesmediterraneo.com/peces-del-mar-mediterraneo/"

_DATA_NAME_MAPPING = {
    "nombre_común": "name",
    "nombre_científico": "scientific_name",
    "descripción": "description",
    "localización": "location",
    "otros_datos": "other_data",
    "comportamiento": "behaviour",
    "talla_mínima_pesca": "min_size_for_catch"
}

@dataclass
class Fish:
        name: str = "",
        scientific_name: str = "",
        description: str = "",
        location: str = "",
        other_data: str = "",
        behaviour: str = "",
        min_size_for_catch: str = "",
        image: str = ""

        def __str__(self):
            return (
                f"Name: {self.name}\n"
                f"Scientific Name: {self.scientific_name}\n"
                f"Description: {self.description}\n"
                f"Location: {self.location}\n"
                f"Other Data: {self.other_data}\n"
                f"Behaviour: {self.behaviour}\n"
                f"Minimum Size for Catch: {self.min_size_for_catch}\n"
                f"Image URL: {self.image}"
            )

def _fetch_page(url: str, timeout: int = 10) -> Optional[BeautifulSoup]:
    try:
        response = requests.get(url, timeout = timeout)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except requests.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        return None

def _save_fish_to_csv(fish_list: list[Fish], filename:str = "fish_data.csv"):
    if not fish_list:
        logger.warning("No fish data to save")
        return None

    from dataclasses import asdict

    data = [asdict(fish) for fish in fish_list]
    df = pd.DataFrame(data)

    df.to_csv(filename, index = False, encoding = 'utf-8')
    logger.info(f"Saved fish data into {filename}")

def _scrap_fish_data(url: str, image: str) -> Optional[Fish]:
    fish = Fish(image = image)

    soup = _fetch_page(url)
    if not soup:
        return None

    results = soup.find("div", class_="caracteristicas")
    if not results:
        logger.error(f"No results found at {url}")
        return None

    for fish_data in results:
        try:
            if not fish_data:
                continue

            data_name = fish_data.find("b")
            if not data_name:
                continue

            data_name = data_name.get_text().replace(":","").strip()

            data_value = fish_data.find(string = True, recursive = False)

            if not data_value:
                try:
                    data_value = fish_data.find_all("p")[1].get_text().replace(":", "").strip()

                except (IndexError, AttributeError) as e:
                    logger.warning(f"Error extracting paragraph: {e}")
                    continue

            data_value = data_value.strip() if data_value else ""

            attribute_name = _DATA_NAME_MAPPING.get(data_name.lower().replace(" ", "_"))

            if attribute_name:
                setattr(fish, attribute_name, data_value)
            else: continue


        except Exception as e:
            logger.exception(f"Error  processing data {fish_data}: {e}")
            continue

    return fish


def main():
    soup = _fetch_page(URL)
    results = soup.find(id="content-wrapper")
    species = results.find_all("div", class_="especie")
    fish_list = []
    for fish in species:
        if not fish:
            continue
        url = fish.find("a")['href']
        image = fish.find("img", src=True)["src"]

        if not url or not image:
            continue
        fish_list.append(_scrap_fish_data(url,image))

    _save_fish_to_csv(fish_list)

if __name__ == "__main__":
    main()
