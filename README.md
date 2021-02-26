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
It's a browser problem, but it should already be fixed with the app config. But you might need to empty the cache or configure Flask to refresh them more explicitly than I did. Or, if you're too lazy for that, copy the source HTML to a static file, direct it to the appropriate CSS file and then work on from there.

### Are you going to add features?
Not really as of now, besides making it look less garish. But the point of this site was just to play around with some Sass and to use a pip package that I'd made. But I do have future plans to design my own icon and maybe something for the backsplash.

### Things to add:
1. Better layout of the flask app

### Changelog:
I'm only adding this beginning in February of 2021
2/17/2021:
> 1. Bug fix: remove "1" in the before pseudoelement of the ingredients on the recipe screen (I accidentally left it in from working on the hover animation)
> 2. Autofocus on input element only occurs on the first page
2/21/2021:
> 1. Added the RM Converter. A plain text mode is forthcoming
2/24/2021:
> 1. Added a plain formatting possibility to reduce load times - no pictures, text in simple flex boxes
> 2. Plain formatting and unit conversion choices will be stored in local storage and loaded appropriately
> 3. Changed align-items from center to flex-start in normal-format recipe
> 4. Added second JS file to initial page titled frontpage.js in order to autofocus the input element upon load
2/25/2021:
> 1. Changed fonts to use a sans and a serif font (hey, I'm trying)
> 2. Changed most colors (I'm not a designer!)
> 3. All illustrations and photos are now of brands or made by me
> 4. Made the checkboxes to slide left-right instead of top-bottom on smaller displays
> 5. Added an error page
> 6. Added an about page
> 7. Added a topbar to navigate to the abovementioned page
2/25/2021 (hotfix/update):
> 1. Changed formatting for mobile on the about page
> 2. Fixed up the error page -- yeah, I'd forgotten about finishing it