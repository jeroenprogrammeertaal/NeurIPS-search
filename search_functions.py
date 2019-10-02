from elasticsearch import Elasticsearch
from elasticsearch import helpers
import nltk.data

def filter_query(filter_values):
    """Generate filter options for elasticsearch query depending on filter input."""
    filter_options = ["authors","title","abstract","paper_text"]
    q = {}
    temp = []
    for option, value in zip(filter_options, filter_values):
        if value != "":
            temp.append({
                "term":{
                    option : value
                }
            })
    return temp

def filter_boolean(filter_values):
    """Generate boolean value depending on filter input."""
    for value in filter_values:
        if value != "":
            return "must"
    return "should"

def search_type(complex_search, query):
    """Generate full text search type, depending on query input."""
    if complex_search == True:
        return {"query_string":{
            "query":"{}".format(query),
            "default_field":"title"
        }}
    return {"multi_match":{
                "query":"{}".format(query),
                "fields":["title", "abstract", "paper_text"]
            }}

def query(es, query='', filter_values=['','','',''], years=(1987, 2017), complex_search=False):
    q = {
        "query":{
            "bool":{
                "must":[
                    search_type(complex_search, query)
                ],
                filter_boolean(filter_values):filter_query(filter_values),
                "filter":{
                     "range":{
                         "year":{
                            "gte":"{}".format(years[0]),
                            "lte":"{}".format(years[1])
                         }
                     }
                 },
            }
        },
        "aggs":{
            "sample":{
                "sampler":{
                    "shard_size": 100
                },
                "aggs":{
                    "keywords":{
                        "significant_text":{
                            "field":"paper_text",
                            "filter_duplicate_text":True
                        }
                    },
                    "years":{
                        "terms":{
                            "field":"year"
                        }
                    }
                },
            }
        }
    }
    return es.search(index='nips_papers_index', body=q, size=100)