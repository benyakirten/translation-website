from flask import Flask, render_template, redirect, url_for, request

import translate_g_z
import apply_translation

app = Flask(__name__, instance_relative_config=True)

# Just something real simple for the translation page
@app.route('/', methods = ('GET', 'POST'))
def welcome():
    if request.method == 'POST':
        recipe = translate_g_z.process_url(request.form['url'])
        trans_recipe = apply_translation.translate_data(recipe)
        return render_template("processed.html",
            title = trans_recipe['name'],
            image = trans_recipe['image'],
            ingredients = trans_recipe['ingredients'],
            prep = trans_recipe['preparation']
        )
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=False)