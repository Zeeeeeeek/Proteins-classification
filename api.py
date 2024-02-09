import requests

REPEATSDB_URL = "https://repeatsdb.bio.unipd.it/api//search"
PDB_URL = "https://files.rcsb.org/download/"


def repeatsdb_get(query):
    r = requests.get(REPEATSDB_URL, params=query)
    return r.json()


def pdb_get(pdb_id):
    return pdb_get_request(pdb_id)


def mmCIF_get(pdb_id):
    return pdb_get_request(pdb_id, file_type='cif')


def pdb_get_request(pdb_id, file_type='pdb'):
    r = requests.get(PDB_URL + pdb_id + "." + file_type)
    if r.status_code == 200:
        return r.text
    return None
