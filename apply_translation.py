import requests, json, os, copy

def translate_data(data):
    """
        This function will take a python dictionary of the following format:
        recipe['name']: string
        recipe['image']: string
        recipe['ingredients']: list of the following format
            [string, float, string]
        recipe['preparation']: list of strings

        And return a dictionary of the same format but having been
        translated by google translate
    """

    # Creating a deep copy so the function doesn't have side effects
    deep_copy = copy.deepcopy(data)

    # Don't steal my API key. I'd be very cross!
    API_KEY = os.environ.get('API_KEY')

    # This program, as explained below, cannot use the google translate module
    # but must instead make get/post requests to the google API, and we are
    # more or less obligated to send the request as a single string.
    # To reduce the amount of requests, there are only two strings requests I'm sending
    # They are both the words/phrases that need translation separated by a %
    ing_string = ''
    for i in deep_copy['ingredients']:
        ing_string += f'{i[0]}% {i[2]}% '
        # i[0] is the name and i[2] is the unit

    prep_string = ''
    for i in deep_copy['preparation']:
        prep_string += f'{i}% '

    # The Python module requires the address to the file containing the credentials
    # And on Heroku, only environment variables are secure. Everything else is on
    # a github repository. Therefore, I wanted to use an API key, which I could
    # store in an environment variable. So I had to do the translation with
    # post requests.
    translated_ing = requests.post(
        f"https://translation.googleapis.com/language/translate/v2/?key={API_KEY}&target=en&source=it&format=text&q={ing_string}"
    )
    translated_prep = requests.post(
        f"https://translation.googleapis.com/language/translate/v2/?key={API_KEY}&target=en&source=it&format=text&q={prep_string}"
    )

    # This is what it would look like if I could:
    # translate_client = translate.Client()
    # translated_ing = translate_client.translate(ing_string,
    #     target_language='en',
    #     source_language='it'
    # )
    # translated_prep = translate_client.translate(prep_string,
    #     target_language='en',
    #     source_language='it'
    # )

    # With the translation done, we convert the return object,
    # a JSON string, into a python dict
    translated_ing = json.loads(translated_ing.content)
    translated_prep = json.loads(translated_prep.content)

    # We are now splitting the data back into lists using the %
    ing_list = translated_ing['data']['translations'][0]['translatedText'].split('%')
    prep_list = translated_prep['data']['translations'][0]['translatedText'].split('%')

    for i in range(len(ing_list)):
        # Occasionally, words will be incorrectly translated
        # This is to catch the worst offenders
        replace_dict = {
            'rib': 'stick',
            'spoons': 'spoonfuls',
            'twigs': 'sprigs',
            'fine salt': 'table salt',
            'n / a': 'n/a',
            'carote': 'carrots',
            'carots': 'carrots'
        }
        temp = ing_list[i].strip()
        if temp.lower() in replace_dict:
            temp = replace_dict[temp.lower()]
        if temp:
            if i % 2 == 0:
                deep_copy['ingredients'][i//2][0] = temp
                # For verbose debugging:
                # try:
                #     deep_copy['ingredients'][i//2][0] = temp
                # except:
                #     print(f"error at ing index: {i}")
                #     print(f"temp = {temp}")
                #     print(f"ing_list = {ing_list}")
                #     print(f"ingredients = {deep_copy['ingredients']}")
            else:
                deep_copy['ingredients'][i//2][2] = temp
                # Idem
                # try:
                #     deep_copy['ingredients'][i//2][2] = temp
                # except:
                #     print(f"error at ing index: {i}")
                #     print(f"temp = {temp}")
                #     print(f"ing_list = {ing_list}")
                #     print(f"ingredients = {deep_copy['ingredients']}")
    
    for i in range(len(prep_list)):
        temp = prep_list[i].strip()
        
        discards = ['. ', ', ', '; ', ': ']
        # I don't know how it's happening, but it is still happening:
        if temp[:2] in discards:
            temp = temp[2:]
        if temp and len(temp) > 1:
            deep_copy['preparation'][i] = temp
            # Again, verbose debugging
            # try:
            #     deep_copy['preparation'][i] = temp
            # except:
            #     print(f"error at prep index: {i}")
            #     print(f"prep_list = {prep_list}")
            #     print(f"prep = {deep_copy['preparation']}")

    return deep_copy