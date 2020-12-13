from flask import Flask, render_template, redirect, url_for, request

import giallo_zafferano
import fatto_di_casa
import apply_translation

app = Flask(__name__, instance_relative_config=True)

@app.route('/', methods = ('GET', 'POST'))
def welcome():
    if request.method == 'POST':
        if request.form['site'] == 'gz':
            recipe = giallo_zafferano.GZConverter(request.form['url'])
        elif request.form['site'] == 'fdc':
            recipe = fatto_di_casa.FCConverter(request.form['url'])
        trans_recipe = apply_translation.translate_data(recipe)

        # To not have them displayed in the template
        for idx in range(len(trans_recipe['ingredients'])):
            if trans_recipe['ingredients'][idx][2] == 'n/a':
                del trans_recipe['ingredients'][idx][2]
        
        return render_template("processed.html",
            title = trans_recipe['name'],
            image = trans_recipe['image'],
            ingredients = trans_recipe['ingredients'],
            prep = trans_recipe['preparation']
        )
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=False)