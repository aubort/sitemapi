import os
import requests
import re
import urllib.parse
import xml.etree.ElementTree as ET
import json

from flask import redirect, render_template, request, session
from functools import wraps


def get_sitemap_as_json(url, method="GET"):
    """
    Crawls a sitemap at the given URL and returns a json object
    Improvement:
    + Use BeautifulSoup since we use it somehwere else now.
    + Better error handling and logging

    """

    # uses the Requests package: https://requests.readthedocs.io/en/master/
    try:
        response = requests.get(url)
        response.raise_for_status()
        xml = response.text

    except requests.RequestException:
        return None

    # we use xml etree to parse the xml from the sitemap https://docs.python.org/3/library/xml.etree.elementtree.html
    # remove the default namespace for simplicity
    root = ET.fromstring(re.sub(r'\sxmlns="[^"]+"', '', xml, count=1))

    urls = []

    # Parse all the elements in the sitemap and converts to a JSON object
    for child in root:
        new_item = {}

        new_item["id"] = int(re.search("\/([a-z0-9_-]*[\/]?)$", child.find(".//loc").text).group(0).replace("/", ""))
        for item in child:
            new_item[item.tag] = item.text

        urls.append(new_item)

    jsonOut = json.dumps(urls, indent=4)

    return jsonOut


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code