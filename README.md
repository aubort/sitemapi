# Goal

Provide a modern REST API for accessing SAP SuccessFactors Job listings using publicly accessible XML sitemaps.


# Background

For a project I am working on, I needed to extract information about open job postings
without having access to some sort of API. The only publicly accessible information provided by the
platform (SAP SuccessFactors) is the xml sitemap.

I figured that it could be possible to write a cwarler/parser of the xml sitemap,
store the information temporarily in a database and then write a REST API that would
allow to retrieve these jobs from the database.

This is what this program is about.

This program is also my final project for my Harvard CS50 class, spring 2020 session.

# How it works

## Crawling

Given a sitemap URL (using a sample job platform for the example: https://careers.swissre.com/sitemap.xml) the crawler will parse the sitemap's XML.
It will store all its attributes in a sqlite database in the `urls` table.

It will check whether the ID already exists in the database, and if it doesn't exist, it will create it.

Once the script has run and all new URLs have been added, it will start the update process.
This function parses all the jobs in the database - which status is either active or unknown -
and gets the title tag from the job posting page (using bs4).

If there is no title, that means the job is already filled and we mark the job as closed.
If we find the title, it updates it in the database. The script could be improved to add
more information (short description, date posted, etc).


## Reading

All the jobs are now accessible with their attributes on the index page. They can be filtered
by status. Accessing the root of the site, is where we can list all the jobs in a pseudo admin page.
Note to self: This should be secured at some point :)


## Displaying the jobs

Using the `/api/jobs/random` endpoint, we can get a random selection of open jobs.
The endpoint returns a json object containing a defined (in the config) number of jobs.

In our `/demo/` page, we are displaying 3 jobs as cards and using "loremp pixel" for the images.
The json response is parsed and rendered with the [Javascript Template Engine](https://github.com/blueimp/JavaScript-Templates).


# Technology

* Backend: Python backend with standard packages. Using additional beautifulsoup for parsing HTML

* Database: sqlite3

* Frontend: Using Jinja templates for the index page which lists all the jobs. Filtering is happening
in the backend using query parameters.
To disply the cards on the demo page, we use plain JS with the Fetch function to get random jobs
from the backend using the API endpoint. In order to display the cards for each job, we use a
lightweight javascript template engine which has no dependency: https://github.com/blueimp/JavaScript-Templates


# (Re)sources

* Inspiration and documentation for the REST API:
https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
* Javascript Template Engine: https://github.com/blueimp/JavaScript-Templates
* Based on CS50's Finance project that I completed: https://cs50.harvard.edu/x/2020/tracks/web/finance/

# Dependencies

Beautifulsoup: pip install beautifulsoup4


# License

This application is released under the
[MIT license](https://opensource.org/licenses/MIT).