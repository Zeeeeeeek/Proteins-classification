import requests

URL = "https://repeatsdb.bio.unipd.it/api//search"


def query_api(query):
    r = requests.get(URL, params=query)
    return r.json()
