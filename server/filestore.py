from dbs import gfs, files
from bson.objectid import ObjectId
from tika import parser
from tesserocr import PyTessBaseAPI
from PIL import Image
import tempfile
import os
api = PyTessBaseAPI()

def createFile(filename, content, case_id_str):
    gfs_id = gfs.put(content, filename=filename)
    file_metadata = {}
    file_metadata['gridfs_id'] = gfs_id
    file_metadata['name'] = filename
    file_metadata['type'] = ''
    file_metadata['extracted_text'] = ''
    file_metadata['case'] = ObjectId(case_id_str)
    r = files.insert_one(file_metadata)
    return r.inserted_id

def runTikaOnFileContent(gridfs_id):
    g = gfs.get(ObjectId(gridfs_id))
    ocrtext = parser.from_buffer(g)
    return ocrtext

def runOcrOnFileContent(gridfs_id):
    g = gfs.get(ObjectId(gridfs_id))
    filename = g.filename
    s = tempfile.NamedTemporaryFile(suffix=os.path.splitext(filename)[1])
    s.write(g.read())
    i = Image.open(s.name)
    api.SetImage(i)
    return api.GetUTF8Text()

