import json, os, copy

def translate_data(data, *, source_language = "it", target_language = "en", client = False, custom_replace = None):
    """
    This function will take a python dictionary of the following format:
    recipe['name']: string
    recipe['image']: string
    recipe['ingredients']: list of the following format
        [string, float, string]
    recipe['preparation']: list of strings

    And return a dictionary of the same format that has been translated by google translate

    If the client is set to true, then it is assumed that you have a service account and the GOOGLE_APPLICATION_CREDENTIALS environment variable if run offline.
    If run on a google-hosted server, this is handled by default.
    For more information consult the documentation at: 
    https://cloud.google.com/translate/docs/setup

    If the client is set to false, it is assumed you have an environment variable set as API_KEY.
    For more information, consult the documentation at:
    https://cloud.google.com/docs/authentication/api-keys

    """
    # Occasionally, the Converter class is given rather than the recipe object
    #   this is to make lives a little easier
    # If an error still arises, then neither the recipe nor the Converter class is valid
    #   for the rest of the operations
    try:
        deep_copy = copy.deepcopy(data)
    except:
        deep_copy = copy.deepcopy(data.recipe)

    ing_string = ''
    for i in deep_copy['ingredients']:
        ing_string += f'{i[0]} % {i[2]} % '
        # i[0] is the name and i[2] is the unit

    prep_string = ''
    for i in deep_copy['preparation']:
        prep_string += f'{i} % '

    if not client:
        import requests
        # An API key must be gotten from google
        API_KEY = os.environ.get('API_KEY')

        # Using an API KEY cannot use the google translate module
        # but must instead make get/post requests to the google API
        # To reduce the amount of requests, only two are made, using string methods
    
        translated_ing = requests.post(
            f"https://translation.googleapis.com/language/translate/v2/?key={API_KEY}&target={target_language}&source={source_language}&format=text&q={ing_string}"
        )
        translated_prep = requests.post(
            f"https://translation.googleapis.com/language/translate/v2/?key={API_KEY}&target={target_language}&source={source_language}&format=text&q={prep_string}"
        )
    else:
        from google.cloud import translate_v2 as translate

        translate_client = translate.Client()
        translated_ing = translate_client.translate(ing_string,
            target_language=target_language,
            source_language=source_language
        )
        translated_prep = translate_client.translate(prep_string,
            target_language=target_language,
            source_language=source_language
        )

    # With the translation done, we convert the return object,
    # a JSON string, into a python dict
    translated_ing = json.loads(translated_ing.content)
    translated_prep = json.loads(translated_prep.content)

    # We are now splitting the data back into lists using the %
    # The POST request will give back a more detailed object
    if not client:
        ing_list = translated_ing['data']['translations'][0]['translatedText'].split('%')
        prep_list = translated_prep['data']['translations'][0]['translatedText'].split('%')
    else:
        ing_list = translated_ing['translatedText'].split('%')
        prep_list = translated_prep['translatedText'].split('%')

    # Occasionally, words will be incorrectly translated
    # This is to catch the worst offenders
    # This could easily be expanded with more examples
    # If so desired, provide a custom_replace dictionary instead of the default
    if custom_replace:
        replace_dict = custom_replace
    else:
        replace_dict = {
            'rib': 'stick',
            'spoon': 'spoonful',
            'twig': 'sprig',
            'fine salt': 'Table salt',
            'n / a': 'n/a',
            'carote': 'carrots',
            'carots': 'carrots'
        }

    # This is for the rare circumstance in which the quantity is a word or contains one
    # I have yet to see if it needs translation or can be handled with its few exceptions
    ingredient_quantity_words = {
        ' o ':' or ',
        'mezzo':'Half'
    }
    shorter = deep_copy['ingredients'].copy()
    for i in range(len(shorter)):
        for word in ingredient_quantity_words.keys():
            if isinstance(shorter[i][1], str) and word in shorter[i][1]:
                deep_copy['ingredients'][i][1] = shorter[i][1].replace(word,ingredient_quantity_words[word])

    for i in range(len(ing_list)):
        temp = ing_list[i].strip()
        if temp.lower() in replace_dict:
            temp = replace_dict[temp.lower()]
        if temp:
            if i % 2 == 0:
                deep_copy['ingredients'][i//2][0] = temp
            else:
                deep_copy['ingredients'][i//2][2] = temp
    
    skipped_steps = 0
    for i in range(len(prep_list)):
        temp = prep_list[i].strip()

        # I'll need to work on this, see why it doesn't work
        # And don't screw up good words
        # for word in replace_dict.keys():
        #     if temp.find(word):
        #         temp.replace(word, replace_dict[word])
        # One last check
        discards = ['. ', ', ', '; ', ': ']
        if temp[:2] in discards:
            temp = temp[2:]
        if temp and len(temp) > 1:
            deep_copy['preparation'][i] = temp
        else:
            if i < len(deep_copy['preparation']):
                skipped_steps += 1
    
    # If there are any skipped steps, this is to ensure that they get eliminated
    # So there are no dangling instructions in the source language
    if skipped_steps > 0:
        deep_copy['preparation'] = deep_copy['preparation'][:-skipped_steps]

    return deep_copy