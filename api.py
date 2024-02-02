import requests

REPEATSDB_URL = "https://repeatsdb.bio.unipd.it/api//search"
PDB_URL = "https://files.rcsb.org/download/"


def repeatsdb_get(query):
    r = requests.get(REPEATSDB_URL, params=query)
    return r.json()


def pdb_get(pdb_id):
    r = requests.get(PDB_URL + pdb_id + ".pdb")
    return r.text
