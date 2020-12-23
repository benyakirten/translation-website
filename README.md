# What is this package about?

It's a simple Flask server to run an applicable recipe through my own r2api package to get the units translated from metric to imperial and then translated. The only two recipe websites that (somewhat) function are Giallo Zafferano and Fatto in Casa da Benedetta. Future converters are planned as well as more functionality, including making the page a SPA instead of a Flask app.

You can see an instantiation of this website at https://g-f-benyakir.herokuapp.com 
Please be gentle and don't use up my translations for the month.

## How do I get it running?
Clone the repository
Then run the following code:
    export FLASK_APP=app.py
    export API_KEY=*your-api-key*
    flask run
OR
    export GOOGLE_APPLICATION_CREDENTIALS=*path-to-google-cloud-translate-credentials-file*
    flask run

### Hey! Why's it giving me an error when I put a recipe in to translate?
There really are two common reasons for an error. Either the recipe parser isn't able to parse the recipe--if so make sure to get rid of all query parameters--but, more likely than not, it's google cloud translate that's a problem.

You need a google cloud translate API key (or if you're running on your computer/hosting the site on a google cloud server, the security credentials). Check out these sites for information:

https://cloud.google.com/translate/docs/languages
https://cloud.google.com/translate/docs/setup
https://cloud.google.com/docs/authentication/api-keys

### Why don't you provide it/one?
It costs money to use google cloud translate after a certain point. If it didn't, I would, readily.

## Why does it look so bad?
I'm not good at design.

## Let me fix the css on my own end. Where are your SASS files?
They're under static (again, Flask). Remember, once you're done editing the SASS, to compile it:
    sass sass/main.scss css/style.css
Or, if you want to do it continuously:
    sass sass/main.scss css/style.css --watch

### Hey, wait! The CSS isn't updating.
It's a browser problem. You need to empty the cache or configure Flask to refresh them. Or, if you're too lazy for that, copy the source HTML to a static file, direct it to the appropriate CSS file and then work on from there.

### Are you going to add features?
Not really as of now, besides making it look less garish. I plan on adding a checkbox if you don't want to convert the units. At that point, it'd probably be easier just to use translate.google.com, but you may prefer the look of this or lack of ads. It's planned for the future, but I have a lot of responsibilities.