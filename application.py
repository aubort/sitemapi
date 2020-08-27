
"""
Main application file for the final project of CS50.

Author: Pascal Aubort, August 2020

This is heavily based on the finance project from the problem set 8

Future Improvements:
+ Add security
+ More async tasks
+ Add logging


"""

import os
import re
import json
import requests
import urllib.parse
import datetime


from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, Response
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from bs4 import BeautifulSoup
from threading import Thread


from helpers import apology, get_sitemap_as_json


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Database name, we use CS50 library
app.config["DB_NAME"] = "sqlite:///sitemap.db"

# Sitemap URL to be crawled
app.config["SITEMAP_URL"] = "https://careers.swissre.com/sitemap.xml"


# Number of jobs returned via the random API
app.config["RANDOM_JOBS_COUNT"] = 3

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure CS50 Library to use SQLite database
db = SQL(app.config["DB_NAME"])


class Crawler():

    def __init__(self):
        self.progress = 0
        self.isDone = False

    def crawl(self):
        locs = get_sitemap_as_json(app.config["SITEMAP_URL"])

        # Get all ids from the database
        ids = db.execute("SELECT id FROM urls")

        # Convert the dict to a simple list of IDs
        ids_list = []
        for val in ids:
            ids_list.append(val['id'])

        # Parse the sitemap and checks if it already exists in the database.
        # if not it creates it
        for i in json.loads(locs):

            if i["id"] not in ids_list:
                query = "INSERT INTO urls (id, loc, is_active) VALUES (?, ?, ?)"
                db.execute(query, i["id"], i["loc"], 1)

        # Inspired from https://stackoverflow.com/questions/41319199/how-do-i-change-the-rendered-template-in-flask-when-a-thread-completes

        th = Thread(target=self.update_jobs, args=())
        th.start()

    def update_jobs(self):
        """
        Update Jobs attributes

        Improvements:
        + Make use of a REST API for updating the jobs
        + Use threading/async

        """

        db = SQL(app.config["DB_NAME"])

        jobs = db.execute("SELECT * FROM urls")

        # Use sessions so that we can keep the connection alive
        s = requests.Session()

        for job in jobs:

            try:
                response = s.get(job['loc'])
                response.raise_for_status()
                content = response.text

            except requests.RequestException:
                return None

            soup = BeautifulSoup(content, features="html5lib")
            title = soup.find_all("span", itemprop="title")

            if len(title) < 1:
                query = "UPDATE urls SET is_active = 0 WHERE id = :id"
                db.execute(query, id=job["id"])

            else:
                query = "UPDATE urls SET title = :title, is_active = 1, updated = :updated WHERE id = :id"
                db.execute(query, title=title[0].get_text(), updated=datetime.datetime.now(), id=job["id"])

        self.isDone = True

    def getProgress(self):
        return self.isDone


crawler = Crawler()


@app.route("/")
def index():
    """Show a table that contains all the active postings"""

    is_active = request.args.get('is_active')

    # default query
    query = ""

    if is_active == "0":
        query = "SELECT * FROM urls WHERE is_active = 0"
    elif is_active == "-1":
        query = "SELECT * FROM urls"
    else:
        query = "SELECT * FROM urls WHERE is_active = 1"

    jobs = db.execute(query)

    return render_template("index.html", jobs=jobs)


@app.route("/demo")
def demo():
    """Show a table that contains all the active postings"""

    # Here we are using pure javascript to get the jobs from the endpoing.
    # No value sent via the render_template function.
    return render_template("demo.html")


@app.route("/crawl")
def crawl():
    """
    Crawl a sitemap via URL and adds URLs in the database


    Improvements:
    + Use some sort of threading/async so that we can see the progress of the crawling as it happens
    + Make use of REST API to create jobs
    """

    crawler.crawl()

    return render_template("crawl.html")


# API


@app.route("/api/crawlstat", methods=["GET"])
def get_crawlstat():
    """Get a list of jobs"""

    return jsonify(crawler.getProgress())


@app.route("/api/jobs", methods=["GET"])
def get_jobs():
    """Get a list of jobs"""

    query = "SELECT * FROM urls"
    result = db.execute(query)
    return jsonify(result)


@app.route("/api/jobs/random", methods=["GET"])
def get_random_jobs():
    """Get a list of random jobs"""

    query = "SELECT * FROM urls WHERE is_active = 1 ORDER BY RANDOM() LIMIT :limit"
    result = db.execute(query, limit=app.config["RANDOM_JOBS_COUNT"])
    return jsonify(result)


@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """Get a job by its id"""

    query = "SELECT * FROM urls WHERE id = :id"
    result = db.execute(query, id=job_id)

    if len(result) < 1:
        resp = jsonify("{}")
        return Response(response={}, status=204, mimetype="application/json")

    return jsonify(result[0])


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
