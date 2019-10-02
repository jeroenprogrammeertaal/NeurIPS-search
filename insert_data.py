# Insterts data from csv into local elasticsearch index
import pandas as pd 
import numpy as np 
from elasticsearch import Elasticsearch
from elasticsearch import helpers

def safe_value(field_val, replace_value):
    """Replaces NaN values with specified replace value."""
    return field_val if not pd.isna(field_val) else replace_value

def clean_text(string):
    """Removes certain characters from string."""
    remove = ['\n','\r','\s','\\']
    if not pd.isna(string):
        for char in remove:
            string = string.replace(char, ' ')
        return string
    else:
        return "Missing"

def filterKeys(document, keys):
    """Translates dataframe to dict for insertion into elasticsearch index."""
    return {key: document[key] for key in keys}

def clean_papers_data(papers):
    """Clean text from papers."""
    papers['abstract'] = papers['abstract'].apply(clean_text)
    papers['paper_text'] = papers['paper_text'].apply(clean_text)
    return papers.drop('event_type', 1)

def merge_to_elastic(paper_authors, papers, authors, index_name):
    """Generator function to merge the three files and insert them into elastic index."""
    columns = list(papers.columns) + ['authors']
    for index, paper in papers.iterrows():
        merger = paper_authors.loc[paper_authors['paper_id'] == index]
        author_ids = merger['author_id'].values
        author_names = [authors.loc[authors['id'] == x, 'name'].values[0] for x in author_ids]
        paper['authors'] = author_names
        yield {
                "_index": index_name,
                "_type": "_doc",
                "_id" : f"{index}",
                "_source": filterKeys(paper, columns),
            }

def insert_to_elastic(elastic, paper_authors, papers, authors, index_name):
    """Inserts data into elasticsearch index"""
    helpers.bulk(elastic, merge_to_elastic(paper_authors, papers, authors, index_name))

if __name__ == "__main__":
    HOST = 'http://localhost:9200/'
    es = Elasticsearch(hosts=[HOST])
    authors = pd.read_csv("Data/authors.csv")
    paper_authors = pd.read_csv("Data/paper_authors.csv")
    papers = pd.read_csv("Data/papers.csv", index_col='id')
    papers = clean_papers_data(papers)
    insert_to_elastic(es, paper_authors, papers, authors, "nips_papers_index")