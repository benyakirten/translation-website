from bs4 import BeautifulSoup
import requests, re, json, copy

from unit_conversion import convert_units_prep, convert_units_ing, float_dot_zero

class GZConverter:
    """
    This class will take a URL of a Giallo Zafferano recipe and return a dictionary of the following format:
    recipe['name']: string
    recipe['image']: string
    recipe['ingredients']: list of the following format
        [string(name), float(quantity), string(unit)]
    recipe['preparation']: list of the steps to make the recipe

    The methods write_soup_to and write_recipe_to writes the soup and recipe
    respectively to the path passed in their arguments, the former as the
    BS4 object prettified, the latter as a JSON object

    Optional parameters: convert_units: bool = True
    If True, units and their quantities in both ingredients and preparation
    will be converted into American imperial units
    If False, they will not be converted
    """
    def __init__(self, url = "https://ricette.giallozafferano.it/Zuppa-di-ceci.html", *, convert_units = True):
    
        # Getting the data from the website
        r = requests.get(url,
            headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})

        self.soup = BeautifulSoup(r.content, 'html.parser')

        self.recipe = {}

        # For the sake of future APIs, the recipe is divided into four parts:

        # The first two are easily findable within the soup
        self.recipe['name'] = self.soup.find('title').text
        # The image will always be the first source with that attribute
        self.recipe['image'] = self.soup.find('source').attrs['data-srcset']
        # We delegate the identification of the ingredients/preparation into separate functions
        self.recipe['ingredients'] = get_ingredients_g_z(self.soup, convert_units)
        self.recipe['preparation'] = get_preparation_g_z(self.soup, convert_units)

    def __repr__(self):
        return f"{self.recipe}"

    def __str__(self):
        ingredients = [f"{i}" for i in self.recipe['ingredients']]
        preparation = [f"{p}" for p in self.recipe['preparation']]
        total_string = f"""
        Name: {self.recipe['name']}\n
        Image: {self.recipe['image']}\n
        Ingredients: {ingredients}\n
        Preparation: {preparation}
        """
        return total_string

    def write_soup_to(self, path):
        """Write the soup to the path"""
        with open(path, 'w') as f:
            f.write(self.soup.prettify())
        
    def write_recipe_to(self, path, indent = 4):
        """Write the recipe to the path as a json object, indent is customizable"""
        with open(path, 'w') as f:
                f.write(json.dumps(self.recipe, indent = indent))

def get_ingredients_g_z(soup, convert_units = True):
    """
    Pass a BeauitfulSoup comprehension of a G-Z recipe with the html.parser
    And get in return a list of the following format:
    [
        [ingredient name, ingredient quantity, ingredient unit],
        [ingredient name, ingredient quantity, ingredient unit],
        etc.
    ]
    The units and quantities will have been converted from metric to imperial units
    This could be rewritten as a tuple for efficiency's sake,
    but it is assumed that it will be modified later in the case of translation.
    """
    final_ingredient_list = []
    ingredients = soup.find_all("dd", {"class": "gz-ingredient"})

    # Other special words may be added, but q.b. is common in Italian
    # while it is not common in English (at least American English)
    # Others are sure to exist, though I don't know them yet
    special_words = {
        'q.b.': 'to taste'
    }

    # This is me trying to be funny, but for the comprehension of units
    # if they use a vulgar fraction will need it to be converted into an
    # amount. I didn't include more because I doubt many recipes include
    # things like 2/5ths of a teaspoon.

    # Any vulgar fraction is uncommon and tends not to be paired with units.
    # Since this is unicode, it could be passed on just fine without
    # conversion into future parts;
    # however, this is a precaution because it could potentially happen
    especially_vulgar_fractions = {
        '¼':1/4,
        '½':1/2,
        '¾':3/4,
        '⅓':1/3,
        '⅔':2/3
    }
    for i in ingredients:
        # Isolate the name, easiest to find in this soup
        name = i.find('a').text.strip()

        # quantity_unit will be one of three formats:
        # QuantityUnit, i.e. 300g
        # (note)QuantityUnit, i.e. (scongelato)300g or scogelato300g
        # SpecialWord, i.e. q.b.
        quantity_unit = i.find('span').text.strip().replace('\t', '').replace('\n', '')
        # This is a search pattern that will put those into three categories
        # 1. group(1) will be the note, as in (scongelato) above
        #     If there is a vulgar fraction, group(1) will be the vulgar fraction
        #         As explained later, this is because of the solution of accepting
        #         both scongelato and (scongelato) for the note
        #     If there is no note and no vulgar fraction (most common outcome),
        #     group(1) will be None
        # 2. group(2) will be the quantity if there isn't a special word (q.b.)
        #     If the special word exists, group(2) will be None
        # 3. group(3) will be the unit or the special word
        #     group(3) should never be none--it would mean the ingredient doesn't have any words
        q_u_regex = re.search('(\(.*\)|\D*)?(\d*[,\./]?[\d]*)(\S*)', quantity_unit)

        # Again, we check if it worked; an blank regex makes the ingredient get appended as []
        if q_u_regex:
            # Special Handling: there is a note

            # An explanation of the case's complexity:
            # group(1) means we suspect there is a note;
            # however, vulgar fractions are counted by regex as letters,
            # not numbers, so it gets caught by the \D*
            # Also note that the parentheses have to be optional because
            # sometimes the note is not written with parenthesies
            # But because of that whole addendum, sometimes group(1)
            # ends up empty but not None
            if q_u_regex.group(1) and q_u_regex.group(1) != '' \
                and q_u_regex.group(1) not in special_words \
                and q_u_regex.group(1) not in especially_vulgar_fractions:
                # Note: the vulgar fractions are counted by regex as letters, not numbers, so it gets caught in the \D*
                name += f" {q_u_regex.group(1)}"
                # The name has already been created, so we append the note to it
                # i.e. pollo -> pollo(scongelato)

            # N.B. how the note is handled, the rest of the if conditions operate
            # independently of it

            # Case 1: there's just a special word, AKA q.b.
            # i.e. q.b. -> group(1) = q.b.; group(2) and (3) = None
            if q_u_regex.group(1) and q_u_regex.group(1) in special_words:
                quantity = special_words[q_u_regex.group(1)]
                unit = 'n/a'
            # Case 2: There's is a vulgar fraction
            # i.e. ¼ -> group(1) = ¼; group(2) and (3) = None;
            # i.e. ¼kg -> group(1) = ¼; group(2) = None; group(3) = kg
            elif q_u_regex.group(1) and q_u_regex.group(1) in especially_vulgar_fractions:
                quantity = especially_vulgar_fractions[q_u_regex.group(1)]
                # This statement is saying: the quantity is equall to the conversion
                # outlined in the especially_vulgar_fractions dictionary
                if q_u_regex.group(3) and q_u_regex.group(3) != '':
                    unit = q_u_regex.group(3)
                else:
                    unit = 'n/a'
            # Case 3: There's a quantity and no unit
            # i.e. 1 -> group(1) = None; group(2) = 1; group(3) = None
            elif q_u_regex.group(2) and not q_u_regex.group(3):
                quantity = q_u_regex.group(2)
                unit = 'n/a'
            # Case 4: Default case (the majority)
            # i.e. 300g -> group(1) = None; group(2) = 300; group(3) = g
            elif q_u_regex.group(2) and q_u_regex.group(3):
                quantity = q_u_regex.group(2)
                unit = q_u_regex.group(3)
        
        # With the units identified, they can be converted
        if convert_units == True:
            quantity, unit = convert_units_ing(quantity, unit)
        # Sometimes the quantity cannot be be rounded because it is not a number
        # even after the conversion

        # This is by far the easiest place to do the .0 to int conversion
        if float_dot_zero(quantity):
            quantity = int(quantity)

        try:
            final_ingredient_list.append([name, round(quantity, 2), unit])
        except:
            final_ingredient_list.append([name, quantity, unit])
    return final_ingredient_list

def get_preparation_g_z(soup, convert_units):
    """
    This function takes a soup of a G-Z recipe and returns the steps
    made into a list with the quantities and units inside converted
    from metric to imperial units
    """
    # N.B. The first part of the search can be discarded for our desires
    temp_steps = soup.find_all("div", {"class": "gz-content-recipe gz-mBottom4x"})
    p = temp_steps[1].find_all('p')
    prep = []

    for i in p:
        # Each paragraph will contain 3 steps
        for j in i:
            # If there isn't an HTML element, we have our instruction
            if not j.name:
                # There will be lots of blank spaces and line breaks in the element
                # idem for the other case
                temp = j.strip().replace('\n','')
                if convert_units == True:
                    temp = convert_units_prep(temp)
                prep.append(temp)
            # If there is, it's an <a> element that links to the general concept of the item
            # the reason why I exclude <span> elements is that they are just the number of the steps
            # this could be refactored to put the photo at each point - which corresponds with the span;
            # however, the reason this isn't done is that it isn't simple to find the photos
            elif j.name != 'span':
                # the a element's text comes always at the end of a step
                # and it is just the name of an ingredient, so it gets
                # appended to the last instruction

                # N.B. this isn't a f string because you can't use \n in them
                prep[-1] += ' ' + j.text.strip().replace('\n', '')
    # This is a complicated list comprehension; I wanted to try it; it's to get rid of '. ' and the like
    # if they begin an instruction; also the instruction should have some content;
    # I don't know how to just do if cases without else in a list comprehension with at least one else
    # N.B. a list comprehension is possible instead of a for loop, but it is somewhat complicated

    # For the list comprehensions we are filtering for 3 things:
    # The first set if statement:
    # 1. Sometimes because of the parsing, the instructions begin with '. ' or the like
    #   i.e. '. E spegnete il fuoco'
    #   This step changes it to 'E spegnete il fuoco'
    # For the end if statements:
    # 2. All instructions should be strings.
    #   They can only be anything else if there is no actual instruction
    # 3. Sometimes the instruction is just a period, etc.  or blank
    discards = ['. ', ', ', '; ', ': ']
    spaceless_discards = ['.', ',', ';', ':']
    prep = [i[2:] if i[:2] in discards else i for i in prep \
        if isinstance(i, str) and i not in spaceless_discards and len(i) > 0]
    return prep