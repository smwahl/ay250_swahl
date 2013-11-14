from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from pybtex.database.input import bibtex
import re
from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy.orm import mapper


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

app.debug = True
collections = []

class Paper(db.Model):
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
    collection    =  db.Column(db.String(120))

    def __init__(self, entry):
        self.citation_tag = entry['citation_tag']
        self.author_list =  entry['author_list']
        self.journal = entry['journal']
        self.volume = entry['volume']
        self.pages = entry['pages']
        self.year = entry['year']
        self.title =  entry['title']       
        self.collection = entry['collection']

# create the database
db.create_all()

def parse_collection(coll,fname):
    '''
    Bibtex parser:
    Takes a string with a name for the new collection, along with the location of the bibtex
    file and adds each entry to the database.
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
                authorlist += '{1}, {0}; '.format(author.first()[0], rx.sub('',author.last()[0]) )
                entry.update({'author_list':authorlist[:-2]})

            # create an entry object and add to database
            new_paper = Paper( entry )
            db.session.add(new_paper)

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

# Details for uploading file using flask
UPLOAD_FOLDER = './uploads/'
ALLOWED_EXTENSIONS = set(['bib'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    '''
    Determine whether the submited file has the correct extension
    '''
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# Website Structure

@app.route('/', methods=['GET', 'POST'])

def site_index():
    '''
    Gives the status of the database, listing the collections currently added. Provides
    links to pages for uploading to and querying the database.
    '''

    # Print status
    if len(collections) > 0:
        text = 'A database is present. These are your available collections:'
    else:
        text = 'No database is present, one has been created for you. '

    # template with links to 
    return render_template('index.html',status_text=text,col_list=collections)

@app.route('/upload', methods=['GET', 'POST'])

def upload_bibtex():
    '''
    Provide a form for uploading a .bib file with a name for the collection. Adds the
    bibtex entries to the database using parse_collection().
    '''

    text = ''
    if request.method == 'POST':

        # get collection name 
        coll = request.form['coll_name']

        # Upload and save file locally
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # run bibtex parser
            collections.append(coll)
            parse_collection(coll,filename)

            # on success return to main page
            return redirect(url_for('site_index'))
        
        # on failure
        else: 
            text = 'Application accepts only BibTeX files with a .bib extension.'

    # Template with form
    return render_template('upload.html',result_text=text)

        

@app.route('/query', methods=['GET', 'POST'])

def query_collection():
    '''
    Provide interface for querying the database by passing an SQL query string.
    '''

    text = 'No Query results to display.'
    if request.method == 'POST':

        # get and form full SQL query
        query = request.form['query']
        sql_cmd = "Select * From Paper WHERE " + query

#         try:
        # execute SQL query
        result = db.engine.execute(sql_cmd)

        # save and view output in an organized fashion
        output = ''
        for row in result:
            for field in ["citation_tag", "author_list","year","title","journal",
                    "volume","pages","collection"]:
                try:
                    output += '{}: {}<br>'.format(field,row[field])
                except:
                    output += '{}: <br>'.format(field)
            output += '<br>'

        if len(output) == 0:
            text = 'No Query results to display.'
        else:
            text = output

        # If a problem encountered
#         except:
#             text = 'Invalid query'

    return render_template('query.html',result_text=text)


if __name__ == "__main__":

    app.run()
 
