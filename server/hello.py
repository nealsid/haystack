from flask import Flask, render_template, redirect, request, make_response
from bson.objectid import ObjectId
from dbs import client, db, files, clients, casescollection, gfs
import filestore
import solrindexing
import savedsearches
import json
import base64
import mimetypes

import gridfs

import tika
tika.initVM()

app = Flask(__name__)

@app.route('/')
def index_page():
    return render_template("mainmenu.html")

@app.route('/clients')
def clients_page():
    all_clients = clients.find()
    return render_template("clients-view.html", clients=all_clients)

@app.route('/client-view')
def clientview():
    client_id = request.args.get('client_id')
    c = clients.find_one({ '_id' : ObjectId(client_id) })
    cases_for_client = casescollection.find({ 'customer' : ObjectId(client_id) })
    return render_template("client-view.html", cases=cases_for_client, client=c)

@app.route('/case-view')
def caseview():
    case_id = ObjectId(request.args.get('case_id'))
    case = casescollection.find_one({ '_id' : case_id })
    casefiles = files.find({ 'case' : case_id })
    client = clients.find_one({ '_id' : case['customer'] })
    initialSearch = request.args.get("initialSearch");
    saved_searches = savedsearches.getAllSavedSearchesForCaseId(case_id)
    return render_template('case-view.html',
                           case=case,
                           case_files=casefiles,
                           client=client,
                           saved_searches=saved_searches,
                           initialSavedSearch=(initialSearch if initialSearch else None))

@app.route('/case-file-search')
def casefilesearch():
    search_term = request.args.get('query')
    case_id = request.args.get('case_id')
    results = solrindexing.searchcasefiles(case_id, search_term)
    results.docs = [x for x in results.docs if x['case_dbid'] == case_id]
    app.logger.info(str(results.docs))
    return render_template('case-search-results.html',
                           results=results)

@app.route('/upload-file', methods=["POST"])
def processFileUpload():
    case_id = request.form['case_id']
    app.logger.info('case id for file upload: ' + str(case_id))
    if request.method != 'POST':
        app.logger.info("method was not post")
        return

    # check if the post request has the file part
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        app.logger.info("no filename")
        return
    if file:
        app.logger.info("creating file")
        f = filestore.createFile(file.filename, file.read(), case_id)
        app.logger.info("creating file return: " + str(f))
    return redirect("/case-view?case_id=" + case_id, code=302)

@app.route('/extract-text-from-file')
def tikaFile():
    gridFsId = request.args.get('file_gridfs_id')
    caseId = files.find_one({ 'gridfs_id':ObjectId(gridFsId)})['case']
    ocrtext = filestore.runTikaOnFileContent(gridFsId)
    solrindexing.indexContentInSolr(caseId, gridFsId, ocrtext['content'])
    return render_template('file-ocr-results.html', ocrtext=ocrtext['content'])

@app.route('/ocr-file')
def ocrFile():
    gridFsId = request.args.get('file_gridfs_id')
    ocrtext = filestore.runOcrOnFileContent(gridFsId)
    app.logger.info("OCR text: " + ocrtext)
    return render_template('file-ocr-results.html', ocrtext=ocrtext)

@app.route('/file-view')
def viewFile():
    gridFsId = request.args.get('file_gridfs_id')
    g = gfs.get(ObjectId(gridFsId))
    file = files.find_one( {'gridfs_id' : ObjectId(gridFsId) })
    case = casescollection.find_one({ '_id' : ObjectId(file['case']) })
    data_url = "/file-download?file_gridfs_id=" + gridFsId
    return render_template('file-view.html', file=file, case=case, data_url=data_url)

@app.route('/file-download')
def downloadFile():
    gridFsId = request.args.get('file_gridfs_id')
    file_metadata = gfs.find_one({ '_id' : ObjectId(gridFsId) })
    filename = file_metadata.filename
    g = gfs.get(ObjectId(gridFsId))
    return (g.read(), { 'Content-Type' : mimetypes.guess_type(filename) })

@app.route('/add-saved-search')
def addSavedSearchForGivenCaseId():
    case_id_str = request.args.get('case_id')
    case_id = ObjectId(case_id_str)
    query = request.args.get('query')
    savedsearches.createSavedSearch([case_id], query)
    return redirect("/case-view?case_id=" + case_id_str + "&initialSearch=" + query, code=302)

@app.route('/delete-saved-search')
def deleteSavedSearch():
    case_id = request.args.get('case_id')
    saved_search_id = request.args.get('id')
    savedsearches.deleteSavedSearchFromCase(saved_search_id, case_id)
    return make_response('', 200)
