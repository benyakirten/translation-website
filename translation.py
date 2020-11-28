from bs4 import BeautifulSoup
import requests, re, json

def giallo_zafferano(url = "https://ricette.giallozafferano.it/Zuppa-di-ceci.html"):
    r = requests.get(url,
        headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})

    soup = BeautifulSoup(r.content, 'html.parser')
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
        quantity, unit = convert_units(quantity, unit)
        try:
            ing.append([name, round(float(quantity), 2), unit])
        except:
            ing.append([name, quantity, unit])
    return ing

def get_preparation_g_z(soup):
    temp_steps = soup.find_all("div", {"class": "gz-content-recipe gz-mBottom4x"})[1:]
    p = temp_steps[0].find_all('p')
    prep = []
    for i in p:
        for j in i:
            if not j.name:
                prep.append(j.strip().replace('\n',''))
            elif j.name != 'span':
                prep[-1] += ' ' + j.text.strip().replace('\n', '')
    prep = [i[2:] if i[:2] == '. ' else i if i != '.' and len(i) > 0 else 1+1 for i in prep]
    prep = [i for i in prep if isinstance(i, str)]
    return prep

def convert_units(quantity, unit):
    # Dict is in the format:
    # key : (ratio, translated_key)
    trans_dict = {
        'g': (0.00220462, 'lb'),
        'grammi': (0.00220462, 'lb'),
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

if __name__ == '__main__':
    giallo_zafferano()