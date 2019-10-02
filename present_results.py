import nltk.data
import numpy as np
from base64 import b64encode
from io import BytesIO
import matplotlib.pyplot as plt
import ipywidgets as widgets
from ipywidgets import interact, interact_manual, GridspecLayout, Layout
from IPython.display import display, Image, HTML
import search_functions

def search_abstract_begin(paper_text, sent_detector):
    """Generate first 5 sentences of abstract of text if abstract value is missing."""
    abstract = paper_text.split("Abstract", 1)
    if len(abstract) < 2:
        accordion = widgets.Accordion(children=[widgets.HTML(value="Document encoding failed...")], selected_index = None)
        accordion.set_title(0, 'Document encoding failed...')
        return accordion
    sents = sent_detector.tokenize(abstract[1])
    accordion = widgets.Accordion(children=[widgets.HTML(value=" ".join(sents[:8])+ "..")], selected_index = None)
    accordion.set_title(0, 'Abstract')
    return accordion

def get_abstract_begin(abstract, paper_text, sent_detector):
    """Generate first 5 sentences of abstract."""
    if abstract.lower() == "abstract missing":
        return search_abstract_begin(paper_text, sent_detector)
    sents = sent_detector.tokenize(abstract.strip())
    accordion = widgets.Accordion(children=[widgets.HTML(value=" ".join(sents))], selected_index = None)
    accordion.set_title(0, 'Abstract')
    return accordion

def add_split_screen(text, iwidth=None):
    """??? """
    figdata = BytesIO()
    plt.savefig(figdata, format='png')
    iwidth = ' width={0} '.format(iwidth) if iwidth is not None else ''
    datatable = '<table><tr><td><img src="data:image/png;base64,{0}"/></td><td>{1}</td></tr></table>'.format(b64encode(figdata.getvalue()).decode(), text)
    return datatable

def get_word_cloud(res):
    """Retrieves the wordcloud from query results."""
    if len(res['aggregations']['sample']['keywords']['buckets']) > 0:
        counter = 0
        list_word_cloud = ['Improve search: <br>']
        for word in res['aggregations']['sample']['keywords']['buckets']:
            counter += 1
            if counter <= 20:
                list_word_cloud.append(word['key'])
    else:
        list_word_cloud = ['']
    return list_word_cloud

out = widgets.Output()

def show_histogram(res):
    """Shows a histogram of the number of results per year, together with the wordcloud."""
    list_word_cloud = get_word_cloud(res)
    if len(res['aggregations']['sample']['years']['buckets']) > 0:
        y = (2017-1986) * [0]
        for word in res['aggregations']['sample']['years']['buckets']:
            y[int(word['key'])-1987] = word['doc_count']
        years_list = [x for x in range(1987,2018,1)]
        barplot = plt.bar(years_list, y)
        plt.yticks(np.arange(0, max(y)+1, step=2))
    text = '<br>'.join(list_word_cloud)
    
    datatable = add_split_screen(text, iwidth='500px')
    display(HTML(datatable))


def print_results(es, sent_detector,query='', filter_values=['','','',''], years=(1987, 2017), complex_search=False):
    """Print results from a search query."""
    res = search_functions.query(es, query, filter_values, years, complex_search)
    print("{} hits".format(res['hits']['total']['value']))
    show_histogram(res)    
    
    for hit in res['hits']['hits']:
        score = round(hit['_score'], 3)
        title_name = hit['_source']['title']
        link_name = "https://papers.nips.cc/paper/" + hit['_source']['pdf_name']
        year = hit['_source']['year']
        author_string = ', '.join(hit['_source']['authors'])
        title_link = widgets.HTML(
            value="<a href='{}' style='font-size: 15px; line-height:1px' target='_blank'>{}</a><span style='color:red; float:right'>Score: {}</span><p style='font-size: 10px; color: grey; line-height:1px'>{} - {}</p>".format(link_name, title_name, score, year, author_string)
        )
        display(title_link)
        display(get_abstract_begin(hit['_source']['abstract'], hit['_source']['paper_text'][:1500], sent_detector))

def generate_logo(file):
    file = open(file, "rb")
    image = file.read()
    logo = widgets.Image(
        value=image,
        format='png',
        width=100,
    )
    return logo

def generate_checkbox(value):
    check = widgets.Checkbox(
        description = value
    )
    return check

def generate_textbox(value, placeholder=''):
    text = widgets.Text(
        description = value
    )
    return text

def generate_button(text):
    button = widgets.Button(
        value=False,
        description=text,
        disabled=False,
        button_style='',
        tooltip=text,
    )
    return button

def generate_slider(value, range_steps):
    slider = widgets.SelectionRangeSlider(
        options = [i for i in range(range_steps[0], range_steps[1], range_steps[2])],
        index=(0,30),
        description=value,
        disabled=False,
        continuous_update=False
    )
    return slider