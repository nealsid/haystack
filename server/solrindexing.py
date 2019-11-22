import pysolr

solr = pysolr.Solr('http://localhost:8983/solr/haystack', timeout=10)

def indexContentInSolr(case_id, file_id, content):
    doc = {
        'id':file_id,
        'case_dbid':case_id,
        'file_text':content
    }
    solr.add([doc], commit=True)
    return

def searchcasefiles(case_id, query):
    query = 'file_text:' + query,

    return solr.search(query, **{
        'hl':'on',
        'hl.fl':'file_text',
        'hl.simple.pre':'<span class=\'highlight\'>',
        'hl.simple.post':'</span>',
        'hl.fragsize':200,
        'wt':'json'
    })
