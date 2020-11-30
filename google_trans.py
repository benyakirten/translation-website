import requests, json, os, copy

def translate_data(data):
    deep_copy = copy.deepcopy(data)

    # Don't steal my API key. I'd be very cross!
    API_KEY = os.environ.get('API_KEY')

    # For the purposes of google translate, this is the easiest way to prepare the data
    # Because the google translate api wants a file with the data or a string
    # With a % as a marker between data sections
    # Note the space after every one: google translate will mess up without it
    ing_string = ''
    for i in deep_copy['ingredients']:
        ing_string += f'{i[0]}% {i[2]}% '

    prep_string = ''
    for i in deep_copy['preparation']:
        prep_string += f'{i}% '

    # Because we're using an API key, we have to do it a little differently
    translated_ing = requests.post(
        f"https://translation.googleapis.com/language/translate/v2/?key={API_KEY}&target=en&source=it&format=text&q={ing_string}"
    )
    translated_prep = requests.post(
        f"https://translation.googleapis.com/language/translate/v2/?key={API_KEY}&target=en&source=it&format=text&q={prep_string}"
    )

    # Creating the client and translating
    # translate_client = translate.Client()
    # translated_ing = translate_client.translate(ing_string,
    #     target_language='en',
    #     source_language='it'
    # )
    # translated_prep = translate_client.translate(prep_string,
    #     target_language='en',
    #     source_language='it'
    # )

    # With the translation done, we convert the JSON string into a python dict
    translated_ing = json.loads(translated_ing.content)
    translated_prep = json.loads(translated_prep.content)

    # we're now splitting the data back into lists
    ing_list = translated_ing['data']['translations'][0]['translatedText'].split('%')
    prep_list = translated_prep['data']['translations'][0]['translatedText'].split('%')

    for i in range(len(ing_list)):
        replace_dict = {
            'rib': 'stick',
            'spoons': 'spoonfuls',
            'twigs': 'sprigs',
            'fine salt': 'Table salt',
            'n / a': 'n/a',
            'CArote': 'carrots',
            'CArots': 'carrots'
        }
        temp = ing_list[i].strip()
        if temp.lower() in replace_dict:
            temp = replace_dict[temp.lower()]
        if temp:
            if i % 2 == 0:
                try:
                    deep_copy['ingredients'][i//2][0] = temp
                except:
                    print(f"error at ing index: {i}")
                    print(f"temp = {temp}")
                    print(f"ing_list = {ing_list}")
                    print(f"ingredients = {deep_copy['ingredients']}")
            else:
                try:
                    deep_copy['ingredients'][i//2][2] = temp
                except:
                    print(f"error at ing index: {i}")
                    print(f"temp = {temp}")
                    print(f"ing_list = {ing_list}")
                    print(f"ingredients = {deep_copy['ingredients']}")
    
    for i in range(len(prep_list)):
        temp = prep_list[i].strip()
        if temp[:2] == '. ' or temp[:2] == ', ':
            temp = temp[2:]
        elif temp == '.' or temp == ',' or temp == ';' or temp == ':':
            temp = ''
        if temp:
            try:
                deep_copy['preparation'][i] = temp
            except:
                print(f"error at prep index: {i}")
                print(f"prep_list = {prep_list}")
                print(f"prep = {deep_copy['preparation']}")

    return deep_copy