from flask import Flask, render_template, redirect, url_for, request
import r2api

app = Flask(__name__, instance_relative_config=True)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

@app.route('/', methods = ('GET', 'POST'))
def welcome():
    if request.method == 'POST':
        try:
            if request.form['convert']:
                convert_units = True
        except:
            convert_units = False

        if request.form['site'] == 'gz':
            recipe = r2api.GZConverter(request.form['url'], convert_units=convert_units)
        elif request.form['site'] == 'fc':
            recipe = r2api.FCConverter(request.form['url'], convert_units=convert_units)
        elif request.form['site'] == 'mz':
            recipe = r2api.MZConverter(request.form['url'], convert_units=convert_units)
        elif request.form['site'] == 'ag':
            recipe = r2api.AGConverter(request.form['url'], convert_units=convert_units)
        elif request.form['site'] == 'rm':
            recipe = r2api.RMConverter(request.form['url'], convert_units=convert_units)
        
        trans_recipe = r2api.translate_data(recipe)

        # To not have display empty units/quantities in the output
        # N.B.: Though it didn't come up before, with the addition of the MZConverter
        # quantities can be n/a too and therefore need to be removed too
        for idx in range(len(trans_recipe['ingredients'])):
            if trans_recipe['ingredients'][idx][1] == 'n/a':
                del trans_recipe['ingredients'][idx][1]
                continue
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