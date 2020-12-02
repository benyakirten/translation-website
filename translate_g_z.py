from bs4 import BeautifulSoup
import requests, re, json, copy

def process_url(url = "https://ricette.giallozafferano.it/Zuppa-di-ceci.html"):
    """
        This function will take a URL of a giallo zafferano site
        and return a dictionary of the following format:
        recipe['name']: string
        recipe['image']: string
        recipe['ingredients']: list of the following format
            [string(name), float(quantity), string(unit)
        recipe['preparation']: list of the steps to make the recipe
        
        Units and their quantities in both ingredients and preparation
        should already be converted into American imperial units
    """
    # Getting the data from the website
    r = requests.get(url,
        headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})

    soup = BeautifulSoup(r.content, 'html.parser')
    
    # Uncomment if you want to examine/save the soup
    # with open('recipe.html', 'w') as f:
    #     f.write(soup.prettify())

    recipe = {}

    # For the sake of future APIs, the recipe is divided into four parts:

    # The first two are easily findable within the soup
    recipe['name'] = soup.find('title').text
    # The image will always be the first source with that attribute
    recipe['image'] = soup.find('source').attrs['data-srcset']
    # We delegate the identification of the ingredients/preparation into separate functions
    recipe['ingredients'] = get_ingredients_g_z(soup)
    recipe['preparation'] = get_preparation_g_z(soup)

    # Just like above, uncomment if you want to see the recipe
    # with open('recipe.json', 'w') as f:
    #     f.write(json.dumps(recipe, indent = 4))

    return recipe

def get_ingredients_g_z(soup):
    """
    Pass a BeauitfulSoup comprehension of a G-Z recipe with the html.parser
    And get in return a list of the following format:
    [
        [ingredient name, ingredient quantity, ingredient unit],
        [ingredient name, ingredient quantity, ingredient unit],
        etc.
    ]
    The units and ingredients have been converted from metric to imperial units
    This could be rewritten as a tuple for efficiency's sake,
    but it is modified later in the google translate file.
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
            # Case 5: else case, used for verbose debugging
            # else:
            #     print('************\nexception case!')
            #     print(f'ingredient: {name}')
            #     if q_u_regex.group(1):
            #         print(f'special:\n{q_u_regex.group(1)}')
            #     else:
            #         print('no special')
            #     if q_u_regex.group(2):
            #         print(f'quantity:\n{q_u_regex.group(2)}')
            #     else:
            #         print('no quantity')
            #     if q_u_regex.group(3):
            #         print(f'unit:\n{q_u_regex.group(3)}')
            #     else:
            #         print('no unit')
            #     print('************')
        
        # Now that we've isolated the units, we will convert them
        quantity, unit = convert_units_ing(quantity, unit)

        # Sometimes the quantity cannot be be rounded because it is not a number
        # even after the conversion
        try:
            final_ingredient_list.append([name, round(quantity, 2), unit])
        except:
            final_ingredient_list.append([name, quantity, unit])
    return final_ingredient_list

def convert_units_ing(quantity, unit):
    """
        Pass in a number and a quantity in metric units
        Returns a number and quantity in (American) imperial units
    """
    # Dict is in the format:
    # key : (ratio, translated_key)
    # Constants are not needed
    # because temperatures are not passed in
    unit_conversion = {
        'g': (0.00220462, 'lb'),
        'grammi': (0.00220462, 'lb'),
        'kg': (2.205, 'lb'),
        'l': (33.8140227, 'fl oz'),
        'litri': (33.8140227, 'fl oz'),
        'ml': (33.8140227 * 1000, 'fl oz'),
        'millilitri': (33.8140227 * 1000, 'fl oz')
    }
    if unit in unit_conversion:
        # The quantity can sometimes contain , instead of .
        # because decimals are written with a comma
        quantity = quantity.replace(',', '.')
        # There is no need for a try/except block because
        # it will be of the proper format if it has gotten this far
        con_q, con_u = (unit_conversion[unit][0] * float(quantity), unit_conversion[unit][1])

        # Sometimes units will be something like .14 lb
        # So they will be converted to oz if they are small enough
        # Or fl oz to cups/quarts if they're large enough
        con_q, con_u = simplify_units(con_q, con_u)
        return con_q, con_u
    else:
        try:
            quantity = float(quantity)
        except:
            pass
        return (quantity, unit)


def get_preparation_g_z(soup):
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

def convert_units_prep(prep):
    """
        Takes a string, parses it for metric units and converts
        both them and the quantities into imperial units and quantities
    """
    # We'll make a copy so we don't have any side effects
    # Because we'll be doing some replacing if we have a hit
    return_string = copy.deepcopy(prep)

    # this dictionary is of the format:
    # key: (scalar, constant, unit)
    # N.B. Both temperatures and lengths are here
    unit_conversions = {
        'g': (0.00220462, 0, 'lb'),
        'grammi': (0.00220462, 0, 'lb'),
        'kg': (2.205, 0, 'lb'),
        'l': (33.814, 0, 'fl oz'),
        'litri': (33.814, 0, 'fl oz'),
        'ml': (33.814 * 1000, 0, 'fl oz'),
        'millilitri': (33.814 * 1000, 0, 'fl oz'),
        '°': (1.8, 32, '°'),
        'cm': (0.3937, 0, 'inches'),
        'mm': (0.03937, 0, 'inches'),
        'm': (39.37, 0, 'inches')
    }
    # When there is a unit, it comes in one of twoformats:
    # 1. quantityunit - i.e. 300g
    # 2. quantity(any of , . / - x)fraction(space)unit - i.e. 1,5 l
    # Regex 3 is so the expression correctly classifies something
    # as the former and the latter as the latter
    # i.e. 1,5l isn't treated as 1, as not a unit and 5l
    # group(1) will always be the quantity, group(2) always the unit
    regex = ['(\d+)([^0-9\s]+)', '(\d+[,\.\/\-x]\d+)[\s](\w*)', '[^,\./-](\d+)[\s](\w+)']
    
    for ex in regex:
        match = re.findall(ex, return_string)
        # it's possible that there are multiple unit conversions in one line
        # i.e. 'mettere 1,5 l di crema con 300g di pollo'
        if len(match) > 0:
            # looping through every match
            for group in match:
                # we will get lots of false positives
                # they'll get ignored if they're not
                # of the appropriate form
                if group[1].lower() in unit_conversions:

                    # We are doing the same replacement that we did above
                    # with . for , so it can be converted to a float
                    if ex == regex[1]:
                        try:
                            amount = float(group[0].replace(',', '.'))
                        # Except occurs if it's not a , but something else
                        # such as - as in 2-3
                        except:
                            digits = re.findall('\d+', group[0])
                            digits = [float(d) for d in digits]
                            amount = (sum(digits) / len(digits))
                            # In this case, we are giving the
                            # average of the numbers; this could be improved
                    else:
                        amount = float(group[0])
                    # The converted quantity is equal to the float times the scalar plus the constant
                    conv_amount = round((amount * unit_conversions[group[1]][0]) + unit_conversions[group[1]][1], 2)
                    # The unit is just the converted unit name
                    conv_unit = unit_conversions[group[1]][2]
                    # We are passing it to the same function to simplify it so we don't have 0.14 lb
                    conv_amount, conv_unit = simplify_units(conv_amount, conv_unit)

                    # This was done to keep the code DRY, but regex[1] and [2] have spaces
                    # that are needed for the matching
                    if ex != regex[0]:
                        replaced_seq = f"{group[0]} {group[1]}"
                        replacing_seq = f"{conv_amount} {conv_unit}"
                    else:
                        replaced_seq = f"{group[0]}{group[1]}"
                        replacing_seq = f"{conv_amount}{conv_unit}"

                    # Every iteration, we're replacing the converted
                    return_string = return_string.replace(replaced_seq, replacing_seq)
    # The process has come to an end
    return return_string

def simplify_units(quantity, unit):
    """
    Takes a quantity and unit in imperial units
    and if it is within certain tolerances, changes it
    to a more convenient quantity
    """
    return_quantity = quantity
    return_unit = unit

    # A large area for improvement is to do rounding based off of the units
    # For example: 1.07lb should really be 1 or 1.2 cups should really be 1
    if unit == 'inches' and quantity >= 12:
        # Convert any quantity over 12 inches to feet and inches
        feet = quantity // 12
        inches = quantity % 12
        return_quantity = f"{feet}'{inches}''"
        return_unit = 'feet'
        if inches > 1:
            return_unit += ' and inches'
    elif unit == 'fl oz' and quantity >= 8:
        # Confort to quart/cup if the quantity is > 32 or > 8
        if quantity >= 32:
            return_quantity= round(quantity/32, 2)
            return_unit = 'quart'
        else:
            return_quantity = round(quantity/8, 2)
            return_unit = 'cup'
    elif unit == 'lb' and quantity < 1:
        # Convert to oz if quantity is less than a pound
        return_quantity = 16 * quantity
        return_unit = 'oz'
    return return_quantity, return_unit