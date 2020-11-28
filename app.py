from flask import Flask, render_template, redirect, url_for, request

import translation
import google_trans

# remember, for development:
# export FLASK_APP=app.py
# export FLASK_DEBUG=1

app = Flask(__name__, instance_relative_config=True)

# Just something real simple for the translation page
@app.route('/', methods = ('GET', 'POST'))
def welcome():
    if request.method == 'POST':
        recipe = translation.giallo_zafferano(request.form['url'])
        trans_recipe = google_trans.translate_data(recipe)
        return render_template("processed.html",
            title = recipe['name'],
            image = recipe['image'],
            ingredients = recipe['ingredients'],
            prep = recipe['preparation']
        )
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=False)