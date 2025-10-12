from bs4 import BeautifulSoup
import requests

URL = "https://pecesmediterraneo.com/peces-del-mar-mediterraneo/"

class Fish:
    name: str
    scientific_name: str
    image: str

    def __init__(self, name: str, scientific_name: str, image: str = ""):
        self.name = name
        self.scientific_name = scientific_name
        self.image = image
    
    def __repr__(self):
        return f"Name: {self.name} Scientific Name: {self.scientific_name} ImageURL: {self.image}"
    
def main():
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="content-wrapper")
    species = results.find_all("div", class_="especie")

    fish_list = list()
    for fish in species:
        img_tag = fish.find(src = True)['src']
        print(img_tag)
        fish_list.append(
            Fish(
                fish.find("h2").text,
                fish.find("div", class_= "nombre").find(text=True, recursive=False).strip(),
                img_tag                
                )
        )

    for fish in fish_list:
        print(fish)



if __name__ == "__main__":
    main()
