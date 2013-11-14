from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from pybtex.database.input import bibtex
import re
from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy.orm import mapper

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

app.debug = True
collections = []

class Paper(db.Model):
# class Paper(object):
    '''
    SQLAlchemy model for a database storing information about a collection of academic papers
    '''
    id = db.Column(db.Integer, primary_key=True)

#     citation_tag  =  db.Column(db.String(120),unique=True)
    citation_tag  =  db.Column(db.String(120))
    author_list   =  db.Column(db.String(120))
    journal       =  db.Column(db.String(60))
    volume        =  db.Column(db.String(12))
    pages         =  db.Column(db.String(24))
    year          =  db.Column(db.Integer)
#     title         =  db.Column(db.String(120),unique=True)
    title         =  db.Column(db.String(120))
    collection    =  db.String(db.String(120))

    def __init__(self, entry):
        self.citation_tag = entry['citation_tag']
        self.author_list =  entry['author_list']
        self.journal = entry['journal']
        self.volume = entry['volume']
        self.pages = entry['pages']
        self.year = entry['year']
        self.title =  entry['title']       
        self.collection = entry['collection']

    def __repr__(self):
        return '{}'.format(self.citation_tag)

db.create_all()

def parse_collection(coll,fname):
    '''
    Bibtex parser based on:
    http://stackoverflow.com/questions/9235853/convert-bibtex-file-to-database-entries-using-python
    '''

    #open a bibtex file
    parser = bibtex.Parser()
    bibdata = parser.parse_file(fname)

    # Extraneous characters to remove from fields before storing
    rx = re.compile('[{}\[\]]')


    #loop through the individual references
    for bib_id in bibdata.entries:
        b = bibdata.entries[bib_id].fields
        citation_tag = bibdata.entries[bib_id].key  

        try:
            # temporarily store entry as a dict
            entry = {}

            entry.update({'citation_tag':citation_tag})
            entry.update({'collection':coll})

            # change these lines to create a SQL insert
            for field in ["title","journal","year","pages","volume"]:
                entry.update({field:rx.sub('',b[field])} )

            #deal with multiple authors
            authorlist=''
            for author in bibdata.entries[bib_id].persons["author"]:
                authorlist += '{1}, {0};'.format(author.first()[0], rx.sub('',author.last()[0]) )
                entry.update({'author_list':authorlist})

            # create an entry object and add to database
#             new_paper = Paper( entry, collname=coll )
#             mapper(Paper, new_table,primary_key=[new_table.c.citation_tag],non_primary=True)
            new_paper = Paper( entry )
            db.session.add(new_paper)


#             engine.execute(new_table.insert(), [entry] )

        # field may not exist for a reference
        except(KeyError):
            continue

    # commit database
    try:
        db.session.commit()
        return 1
    except:
        return 0

# for uploading file
import os
from flask import Flask, request, redirect, url_for, render_template
from werkzeug import secure_filename

UPLOAD_FOLDER = './uploads/'
ALLOWED_EXTENSIONS = set(['bib'])

# app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def site_index():
    if len(collections) > 0:
        text = 'A database is present. These are your available collections:'
    else:
        text = 'No database is present, one has been created for you. '

    return render_template('index.html',status_text=text,col_list=collections)

@app.route('/upload', methods=['GET', 'POST'])
def upload_bibtex():
    text = ''
    if request.method == 'POST':
        coll = request.form['coll_name']
#         file = request.files['file']
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # run bibtex parser
            collections.append(coll)
            parse_collection(coll,filename)

            return redirect(url_for('site_index'))
        else:
            text = 'Application accepts only BibTeX files with a .bib extension.'

    return render_template('upload.html',result_text=text)

        

@app.route('/query', methods=['GET', 'POST'])
def query_collection():
    text = 'No Query results to display.'
    if request.method == 'POST':
        query = request.form['query']
        sql_cmd = "Select * From Paper WHERE " + query
        try:
            result = db.engine.execute(sql_cmd)
            output = ''
            for row in result:
                output += repr(row)  + '\n' 

            if len(output) == 0:
                text = 'No Query results to display.'
            else:
                text = output
        except:
            text = 'Invalid query'

    return render_template('query.html',result_text=text)


if __name__ == "__main__":

    app.run()
 
