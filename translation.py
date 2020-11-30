from bs4 import BeautifulSoup
import requests, re, json, copy

def giallo_zafferano(url = "https://ricette.giallozafferano.it/Zuppa-di-ceci.html"):
    r = requests.get(url,
        headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})

    soup = BeautifulSoup(r.content, 'html.parser')
    
    # This is if you want to examine the soup
    # Make sure it is not deployed to the server!
    # with open('recipe.html', 'w') as f:
    #     f.write(soup.prettify())

    recipe = {}

    recipe['name'] = soup.find('title').text
    recipe['image'] = soup.find('source').attrs['data-srcset']
    recipe['ingredients'] = get_ingredients_g_z(soup)
    recipe['preparation'] = get_preparation_g_z(soup)

    # If you want to see what the recipe looks like
    # with open('test.json', 'w') as f:
    #     f.write(json.dumps(recipe, indent = 4))

    return recipe

def get_ingredients_g_z(soup):
    ing = []
    ingredients = soup.find_all("dd", {"class": "gz-ingredient"})
    special_words = {
        'q.b.': 'to taste'
    }
    especially_vulgar_fractions = {
        '¼':1/4,
        '½':1/2,
        '¾':3/4,
        '⅓':1/3,
        '⅔':2/3
    }
    for i in ingredients:
        name = i.find('a').text.strip()
        quantity_unit = i.find('span').text.strip().replace('\t', '').replace('\n', '')
        a = re.search('(\(.*\)|\D*)?(\d*[,\./]?[\d]*)(\S*)', quantity_unit)
        # these are the various options I found:
        if a:
            # If there is a special instruction, it gets appended to the name
            if a.group(1) and a.group(1) != '' and a.group(1) not in special_words and a.group(1) not in especially_vulgar_fractions:
                name += f" {a.group(1)}"
            # If there's just a special word, AKA q.b.
            if a.group(1) and a.group(1) in special_words:
                quantity = special_words[a.group(1)]
                unit = 'n/a'
            # If it's a special character (like ½)
            elif a.group(1) and a.group(1) in especially_vulgar_fractions:
                quantity = a.group(1)
                unit = 'n/a'
            # If there's only a quantity and no unit
            elif a.group(2) and not a.group(3):
                quantity = a.group(2)
                unit = 'n/a'
                # I'll have to reconsider how ingredients are a datastructure
            # this is basically the default case
            elif a.group(2) and a.group(3):
                quantity = a.group(2)
                unit = a.group(3)
            # else case is for if there's something I hadn't planned for
            else:
                print('************\nexception case!')
                print(f'ingredient: {name}')
                if a.group(1):
                    print(f'special:\n{a.group(1)}')
                else:
                    print('no special')
                if a.group(2):
                    print(f'quantity:\n{a.group(2)}')
                else:
                    print('no quantity')
                if a.group(3):
                    print(f'unit:\n{a.group(3)}')
                else:
                    print('no unit')
                print('************')
        if quantity in especially_vulgar_fractions:
            quantity = especially_vulgar_fractions[quantity]
        quantity, unit = convert_units_ing(quantity, unit)
        try:
            ing.append([name, round(float(quantity), 2), unit])
        except:
            ing.append([name, quantity, unit])
    return ing

def get_preparation_g_z(soup):
    # This gets the div with all the steps in it; the first item in the array
    # it has two parts: some formal stuff we don't care about and the content
    # We're cutting the first part out. This could be refactored.
    temp_steps = soup.find_all("div", {"class": "gz-content-recipe gz-mBottom4x"})[1:]
    # Now we take the meat and find all the P elements in it
    p = temp_steps[0].find_all('p')
    prep = []
    # There are several p elements
    for i in p:
        # In each of them, we're looking for elements in them
        for j in i:
            # If there isn't one, we add it to our array
            if not j.name:
                temp = j.strip().replace('\n','')
                temp = convert_units_prep(temp)
                prep.append(temp)
            # If there is, it's an <a> element that links to the general concept of the item
            # the reason why I exclude <span> elements is that there are many of them
            # and they just are numbers that number the steps
            # this could be refactored to put the photo at each point - which corresponds with the span
            elif j.name != 'span':
                # this isn't a f string because you can't use \n in them
                prep[-1] += ' ' + j.text.strip().replace('\n', '')
    # This is a complicated list comprehension; I wanted to try it; it's to get rid of '. ' and the like
    # if they begin an instruction; also the instruction should have some content;
    # I don't know how to just do if cases without else in a list comprehension with at least one else
    prep = [i[2:] if i[:2] == '. ' or i[:2] == ', ' or i[:2] == ': ' or i[:2] == '; ' else i if i != '.' and len(i) > 0 else 1+1 for i in prep]
    # I don't want any elements that are a number
    prep = [i for i in prep if isinstance(i, str)]
    return prep

def convert_units_ing(quantity, unit):
    # Dict is in the format:
    # key : (ratio, translated_key)
    trans_dict = {
        'g': (0.00220462, 'lb'),
        'grammi': (0.00220462, 'lb'),
        'kg': (2.205, 'lb'),
        'l': (33.8140227, 'fl oz'),
        'litri': (33.8140227, 'fl oz'),
        'ml': (33.8140227 * 1000, 'fl oz'),
        'millilitri': (33.8140227 * 1000, 'fl oz')
    }
    if unit in trans_dict:
        # Converting , to . for other languages
        if quantity.find(',') != -1:
            quantity = quantity.replace(',', '.')
        con_q, con_u = (trans_dict[unit][0] * float(quantity), trans_dict[unit][1])
        if con_q < 0.5 and con_u == 'lb':
            con_q = 16 * con_q
            con_u = 'oz'
        if con_u == 'fl oz':
            if con_q > 32:
                con_q = con_q/32
                con_u = 'quart'
            elif con_q > 8:
                con_q = con_q/8
                con_u = 'cup'
        return con_q, con_u
    else:
        return (quantity, unit)

def convert_units_prep(prep):
    # We'll make a copy so we don't have any side effects
    return_string = copy.deepcopy(prep)

    # this dictionary is of the format:
    # scalar, constant, unit
    trans_dict = {
        'g': (0.00220462, 0, 'lb'),
        'grammi': (0.00220462, 0, 'lb'),
        'kg': (2.205, 0, 'lb'),
        'l': (33.8140227, 0, 'fl oz'),
        'litri': (33.8140227, 0, 'fl oz'),
        'ml': (33.8140227 * 1000, 0, 'fl oz'),
        'millilitri': (33.8140227 * 1000, 0, 'fl oz'),
        '°': (1.8, 32, '°'),
        'cm': (0.39370079, 0, 'inches'),
        'mm': (0.03937008, 0, 'inches')
    }
    regex = ['(\d+)(\w+)', '(\d+[,\./-x]\d+)[\s](\w*)', '[^,\./-](\d+)[\s](\w+)']
    
    for ex in regex:
        match = re.findall(ex, return_string)
        if len(match) > 0:
            for group in match:
                # group 1 is always the unit
                if group[1].lower() in trans_dict:
                    # This is a hacky solution that
                    # Convert the str to a float
                    amount = float(group[0])
                    # Convert the quantities
                    # it's equal to the float times the scalar plus the constant
                    conv_amount = round((amount * trans_dict[group[1]][0]) + trans_dict[group[1]][1], 2)
                    conv_unit = trans_dict[group[1]][2]

                    # Convert the quantities according to convenient imperial units
                    if conv_unit == 'inches' and conv_amount > 12:
                        # Convert any amount over 12 inches to feet and inches
                        feet = conv_amount // 12
                        inches = conv_amount % 12
                        conv_amount = f"{feet}'{inches}''"
                        conv_unit == 'feet and inches'
                    if conv_unit == 'fl oz' and conv_amount > 8:
                        # Confort to quart/cup if the amount is large enough
                        if conv_amount > 32:
                            conv_amount = round(conv_amount/32, 2)
                            conv_unit = 'quart'
                        conv_amount = round(conv_amount/8, 2)
                        conv_unit = 'cup'
                    if conv_unit == 'lb' and conv_amount < 1:
                        # Convert to oz if quantity is less than a pound
                        conv_amount = 8 * conv_amount
                        conv_unit = 'oz'
                    if ex.find('\s') != -1:
                        replaced_seq = f"{group[0]} {group[1]}"
                        replacing_seq = f"{conv_amount} {conv_unit}"
                    else:
                        replaced_seq = f"{group[0]}{group[1]}"
                        replacing_seq = f"{conv_amount}{conv_unit}"

                    return_string = return_string.replace(replaced_seq, replacing_seq)
    return return_string

if __name__ == '__main__':
    giallo_zafferano()