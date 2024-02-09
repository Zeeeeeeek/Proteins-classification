import os

if not os.path.exists("log"):
    os.makedirs("log")

if not os.path.exists("csv"):
    os.makedirs("csv")

if not os.path.exists("kmers"):
    os.makedirs("kmers")