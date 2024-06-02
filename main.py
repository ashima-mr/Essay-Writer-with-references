from openai import OpenAI
from dev import openai_api_key 

client = OpenAI(api_key=openai_api_key)

def generate_essay(topic, max_length=1000):
    response = client.completions.create(engine="gpt-3.5-turbo",
    prompt=f"Write an essay on {topic}",
    max_tokens=max_length,
    n=1,  # Number of completions to generate
    stop=None,  # No stopping condition
    temperature=0.5,  # Adjust based on desired output style
    presence_penalty=0)
    essay = response.choices[0].text.strip()
    return essay

from scholarly import scholarly

def fetch_academic_references(topic):
    search_query = scholarly.search_pubs(topic)
    references = []
    for i in range(5):  # Get top 5 papers
        try:
            paper = next(search_query)
            references.append({
                'title': paper.bib['title'],
                'author': paper.bib['author'],
                'journal': paper.bib['journal'],
                'year': paper.bib['pub_year'],
                'url': paper.bib['url']
            })
        except StopIteration:
            break
    return references

import arxiv

def fetch_academic_references_arxiv(topic):
    search = arxiv.Search(
        query=topic,
        max_results=5,
        sort_by=arxiv.SortCriterion.Relevance
    )
    references = []
    for result in search.results():
        references.append({
            'title': result.title,
            'author': ', '.join([author.name for author in result.authors]),
            'journal': 'arXiv',
            'year': result.published.year,
            'url': result.entry_id
        })
    return references

import citeproc
from citeproc import CitationStylesStyle, CitationStylesBibliography, formatter
from citeproc.source.json import CiteProcJSON

def format_references_academic(references):
    csl = CitationStylesStyle('apa', locale='en-US')
    bib_source = CiteProcJSON([{
        "id": str(i),
        "type": "article-journal",
        "title": ref['title'],
        "author": [{"literal": ref['author']}],
        "issued": {"date-parts": [[ref['year']]]},
        "URL": ref['url']
    } for i, ref in enumerate(references)])
    bibliography = CitationStylesBibliography(csl, bib_source, formatter.html)
    formatted_references = [str(entry) for entry in bibliography.bibliography()]
    return formatted_references

def create_essay_with_academic_references(topic):
    essay = generate_essay(topic)
    references = fetch_academic_references(topic)  # Or use fetch_academic_references_arxiv
    formatted_references = format_references_academic(references)
    return essay, formatted_references
