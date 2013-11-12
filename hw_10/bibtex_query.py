from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
# import pybtex

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

app.debug = True

'''
Bibtex parser based on:
http://stackoverflow.com/questions/9235853/convert-bibtex-file-to-database-entries-using-python
'''

from pybtex.database.input import bibtex

#open a bibtex file
parser = bibtex.Parser()
bibdata = parser.parse_file("homework_10_refs.bib")

#loop through the individual references
for bib_id in bibdata.entries:
    b = bibdata.entries[bib_id].fields
    try:
        # change these lines to create a SQL insert
        print b["title"]
        print b["journal"]
        print b["year"]
        #deal with multiple authors
        for author in bibdata.entries[bib_id].persons["author"]:
            print author.first(), author.last()
    # field may not exist for a reference
    except(KeyError):
        continue
