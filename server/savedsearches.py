from dbs import db, savedsearches
from bson.objectid import ObjectId
import solrindexing

def createSavedSearch(case_ids, query):
    existing_query = savedsearches.find_one({ 'query':query})
    if existing_query is None:
        savedsearches.insert_one({
            'query': query,
            'case_ids': [ObjectId(x) for x in case_ids]
        })
    else:
        existing_query['case_ids'].extend(case_ids)
        existing_query['case_ids'] = list(set(existing_query['case_ids']))
        savedsearches.update({'_id':ObjectId(existing_query['_id'])},
                             existing_query)

def runSavedSearch(saved_search_id):
    savedsearch = savedsearches.find_one({ '_id': ObjectId(saved_search_id)})
    results = solrindexing.searchcasefiles(savedsearch['case_ids'], savedsearch['query'])
    if saved_search_is_different(savedsearch.results,
                                 results):
        savedsearches.update({'_id':ObjectId(saved_search_id)},
                             {'results': results})
        return True

    return False

def getAllSavedSearchesForCaseId(case_id):
    savedsearch = savedsearches.find({ 'case_ids': { '$eq' : case_id }})
    return savedsearch

def deleteSavedSearchFromCase(saved_search_id, case_id):
    savedsearch = savedsearches.find_one({ '_id': ObjectId(saved_search_id)})
    existing_case_ids = savedsearch['case_ids']
    if len(existing_case_ids) == 1 and existing_case_ids[0] == ObjectId(case_id):
        savedsearches.find_one_and_delete({ '_id': ObjectId(saved_search_id)})
        return
    else:
        existing_case_ids.remove(ObjectId(case_id))
        savedsearches.update({ '_id':ObjectId(saved_search_id) },
                             savedsearch)
    return
