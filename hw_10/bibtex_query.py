from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from pybtex.database.input import bibtex
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

app.debug = True

class paper(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    citation_tag = db.Column(db.String(120),unique=True)
    author_list = db.Column(db.String(120))
    journal = db.Column(db.String(60))
    volume = db.Column(db.String(12))
    pages = db.Column(db.String(24))
    year = db.Column(db.Integer)
    title = db.Column(db.String(120),unique=True)
    collection = db.String(db.String(120))



'''
Bibtex parser based on:
http://stackoverflow.com/questions/9235853/convert-bibtex-file-to-database-entries-using-python
'''

from pybtex.database.input import bibtex

#open a bibtex file
parser = bibtex.Parser()
bibdata = parser.parse_file("homework_10_refs.bib")

# Extraneous characters to remove from fields before storing
rx = re.compile('[{}\[\]]')

coll_name='my_collection'

#loop through the individual references
for bib_id in bibdata.entries:
    b = bibdata.entries[bib_id].fields
    citation_tag = bibdata.entries[bib_id].key  

    try:
        # temporarily store entry as a dict
        entry = {}

        entry.update({'citation_tag':citation_tag})
        entry.update({'collection':coll_name})

        # change these lines to create a SQL insert
        for field in ["title","journal","year","pages","volume"]:
            entry.update({field:rx.sub('',b[field])} )

        #deal with multiple authors
        authorlist=''
        for author in bibdata.entries[bib_id].persons["author"]:
            authorlist += '{1}, {0};'.format(author.first()[0], rx.sub('',author.last()[0]) )
            entry.update({'author_list':authorlist})

#         print entry

    # field may not exist for a reference
    except(KeyError):
        continue


