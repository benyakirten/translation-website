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
There really are two common reasons for an error. Either the recipe parser isn't able to parse the recipe--if so make sure to get rid of all query parameters on the recipe--but, more likely than not, it's google cloud translate that's a problem.

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

### API Requests (recipe as plain JSON):
The website accept GET and POST requests made to the /api URL and returns the recipe as a JSON object. The parameters (or query variables if it's a GET request) it accepts are below:
1. url -- NECESSARY: this is the url of the recipe you are attempting to translate
2. converter -- OPTIONAL (default: the appropriate type of converter will be guessed at using the same method as the form on the website): the type of converter to be used. Accepted values are: gz, fc, mz, ag, rm
3. convertUnits -- OPTIONAL (default: True): this is if you want the units converted from metric to imperial. Values of true, True, yes, 1, y will set the convert_units property to True. All others will set the property to False.
4. translate -- OPTIONAL (default: True): if you want the recipe translated to English. Values of true, True, yes, 1, y will set the convert_units property to True. All others will set the property to False.

### Future changes:
1. Better accessibility/SEO

### Changelog:
These have only been tracked since February 2021:
* 2/17/2021:
> 1. Bug fix: remove "1" in the before pseudoelement of the ingredients on the recipe screen (I accidentally left it in from working on the hover animation)
> 2. Autofocus on input element only occurs on the first page
* 2/21/2021:
> 1. Added the RM Converter. A plain text mode is forthcoming
* 2/24/2021:
> 1. Added a plain formatting possibility to reduce load times - no pictures, text in simple flex boxes
> 2. Plain formatting and unit conversion choices will be stored in local storage and loaded appropriately
> 3. Changed align-items from center to flex-start in normal-format recipe
> 4. Added second JS file to initial page titled frontpage.js in order to autofocus the input element upon load
* 2/25/2021:
> 1. Changed fonts to use a sans and a serif font (hey, I'm trying)
> 2. Changed most colors (I'm not a designer!)
> 3. All illustrations and photos are now of brands or made by me
> 4. Made the checkboxes to slide left-right instead of top-bottom on smaller displays
> 5. Added an error page
> 6. Added an about page
> 7. Added a topbar to navigate to the abovementioned page
* 2/25/2021 (hotfix/update):
> 1. Changed formatting for mobile on the about page
> 2. Fixed up the error page -- yeah, I'd forgotten about finishing it
* 2/26/2021:
> 1. I know, too many commits/changes in too quick of a time. I keep noticing small things that somehow eluded my attention before. This should be the last update for awhile unless I also update r2api.
> 2. Made it so on the first time loading the page, the text doesn't read as undefined
> 3. Added text underneath the link pictures on the About page for phone displays (since they cannot hover elements)
> 4. Added a few fun hover animations for the main bar
> 5. Added an API route for retrieving the data as JSON. Details of how to use it are above under API Requests.
* 3/1/2021:
> 1. Yes, I really forgot to put an alt caption on the logo image of the header. Changed a transform-origin to left instead of 0 0
* 3/24/2021:
> 1. I've been busy with other things, but I did notice the favicon was unnecessarily large. This has been corrected.
> 2. Let's try that again.
* 3/30/2021:
> 1. Updated packages because urllib3 and Jinja2 had a vulnerability.
* 7/28/2021:
> 1. Enabled CORS for the API route
> 2. Updated urllib3 again (finally)
* 10/11/2021:
> 1. Removed google translate dependencies that served no purpose
> 2. Prepared the repository to be deployed to Heroku via container
> 3. I may update the stylings in the future to be more accessible and add some meta tags for SEO