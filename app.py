from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    jsonify
)
from werkzeug.exceptions import HTTPException
import re
import r2api

app = Flask(__name__, instance_relative_config=True)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/', methods = ('GET', 'POST'))
def welcome():
    if request.method == 'POST':
        try:
            if request.form['convert']:
                convert_units = True
        except:
            convert_units = False

        try:
            if request.form['simple']:
                recipe_format = 'processed'
        except:
            recipe_format = 'plain'

        recipe = _converter_applied(request.form['url'], request.form['site'], convert_units)

        # Potentially we could add a dial to the form to not translate a recipe
        trans_recipe = r2api.translate_data(recipe)

        # Provide a fallback image if the converter can't find a photo
        if not re.search(r'\.\w+$', trans_recipe['image']):
            trans_recipe['image'] = 'static/img/Background.svg'

        # To not have display empty units/quantities in the output
        # N.B.: Though it didn't come up before, with the addition of the MZConverter
        # quantities can be n/a too and therefore need to be removed too
        for idx in range(len(trans_recipe['ingredients'])):
            if trans_recipe['ingredients'][idx][1] == 'n/a':
                del trans_recipe['ingredients'][idx][1]
                continue
            if trans_recipe['ingredients'][idx][2] == 'n/a':
                del trans_recipe['ingredients'][idx][2]
        
        return render_template(f'{recipe_format}.html',
            title = trans_recipe['name'],
            image = trans_recipe['image'],
            ingredients = trans_recipe['ingredients'],
            prep = trans_recipe['preparation']
        )
    return render_template('index.html')

@app.route('/api', methods = ['POST'])
def api():
    TRUE_STRINGS = ['True', 'true', '1', 'y', 'yes']
    WEBSITE_TO_VALUE = {
        "ricette.giallozafferano": "gz",
        "fattoincasa": "fc",
        "mollichedizucchero": "mz",
        "allacciateilgrembiule": "ag",
        "primipiattiricette": "rm",
    }

    recipe_json_data = request.get_json(force=True)

    url = recipe_json_data['url']

    # Default values for the API
    try:
        converter_type = recipe_json_data['converter']
    except:
        for key, value in WEBSITE_TO_VALUE.items():
            if key in url:
                converter_type = value
    
    try:
        if recipe_json_data['convertUnits'] in TRUE_STRINGS:
            convert_units = True
        else:
            convert_units = False
    except:
        convert_units = True
    
    try:
        if recipe_json_data['translate'] in TRUE_STRINGS:
            translate_recipe = True
        else:
            translate_recipe = False
    except:
        translate_recipe = True

    recipe = _converter_applied(url, converter_type, convert_units)

    if translate_recipe:
        recipe = r2api.translate_data(recipe)
    else:
        recipe = recipe.recipe

    return jsonify(recipe)

def _converter_applied(url, converter_name, convert_units = True):
    if converter_name == 'gz':
        return r2api.GZConverter(url, convert_units=convert_units)
    elif converter_name == 'fc':
        return r2api.FCConverter(url, convert_units=convert_units)
    elif converter_name == 'mz':
        return r2api.MZConverter(url, convert_units=convert_units)
    elif converter_name == 'ag':
        return r2api.AGConverter(url, convert_units=convert_units)
    elif converter_name == 'rm':
        return r2api.RMConverter(url, convert_units=convert_units)

    # If none of the converters work, an exception is raised
    raise AttributeError('Converter type not recognized')

@app.route('/about', methods = ['GET'])
def about():
    return render_template('about.html')

@app.errorhandler(HTTPException)
def handle_exception(e):
    return render_template('error.html')

if __name__ == '__main__':
    app.run(debug=False)