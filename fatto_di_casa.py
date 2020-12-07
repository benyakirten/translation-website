from bs4 import BeautifulSoup
import requests, re, json, copy

from unit_conversion import convert_units_prep, convert_units_ing, float_dot_zero

class FCConverter:
    def __init__(self, url = "https://www.fattoincasadabenedetta.it/ricetta/gnocchi-filanti-alla-sorrentina/", *, convert_units = True):
        r = requests.get(url,
            headers = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
        
        self.soup = BeautifulSoup(r.content, 'html.parser')

        self.recipe = {}

        # For the sake of future APIs, the recipe is divided into four parts:

        # The first two are easily findable within the soup
        self.recipe['name'] = self.soup.find('title').text
        # The image will always be the first source with that attribute
        self.recipe['image'] = self.soup.find('img', {'id': 'top-img'}).attrs['src']
        # We delegate the identification of the ingredients/preparation into separate functions
        self.recipe['ingredients'] = get_ingredients_f_c(self.soup, convert_units)
        self.recipe['preparation'] = get_preparation_f_c(self.soup, convert_units)

    def __repr__(self):
        return f"{self.recipe}"

    def write_soup_to(self, path):
        """Write the soup to the path"""
        with open(path, 'w') as f:
            f.write(self.soup.prettify())
        
    def write_recipe_to(self, path, indent = 4):
        """Write the recipe to the path as a json object, indent is customizable"""
        with open(path, 'w') as f:
                f.write(json.dumps(self.recipe, indent = indent))

def get_ingredients_f_c(soup, convert_units):
    ing_elements = soup.find_all('li', {'class': 'wpurp-recipe-ingredient'})
    ingredients = []
    quantities = []
    units = []
    for element in ing_elements:
        quantity = element.find('span', {'class': 'wpurp-recipe-ingredient-quantity'}).text
        unit = element.find('span', {'class': 'wpurp-recipe-ingredient-unit'}).text
        name = element.find('span', {'class': 'wpurp-recipe-ingredient-name'})
        children = name.findChildren()
        # Sometimes these are notes; at other times they're quantities 
        if len(children) > 0 and re.search('\d+', children[0].text):
            # This tests for that situation
            quantity = children[0].text
            unit = 'n/a'
            name = name.text
            name = name.replace(quantity, '')
            quantity = quantity.replace("(", "").replace(")", "")
        else: name = name.text

        # If it's a special word
        special_words = ['q.b.', 'a piacere']
        for word in special_words:
            if word in name:
                name = name.replace(word, '')
                quantity = word
                unit = 'n/a'
        if len(unit) == 0:
            unit = 'n/a'
        if len(quantity) == 0:
            quantity = 'n/a'
        name = name.strip()

        "Let's just take out the 'di' and pass the rest of the sentence"
        if name[:3] == "di ":
            name = name[3:].capitalize()

        if convert_units:
            quantity, unit = convert_units_ing(quantity, unit)

        if float_dot_zero(quantity):
            quantity = int(quantity)

        ingredients.append([name, quantity, unit])
    return ingredients

def get_preparation_f_c(soup, convert_units):
    elements = soup.find_all("li", {"class": "wpurp-recipe-instruction"})
    prep = []
    for step in elements:
        temp = step.text.strip().replace("\n", " ")
        if convert_units:
            temp = convert_units_prep(temp)
        if len(temp) > 0:
            prep.append(temp)
    return prep

