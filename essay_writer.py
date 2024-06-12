import streamlit as st
import os
import openai
from openai import OpenAI
from scholarly import scholarly
import arxiv
from arxiv import Client, Search, SortCriterion
import requests
from io import BytesIO
import PyPDF2
import re
from bs4 import BeautifulSoup

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

"""# Google Scholar"""

def fetch_academic_references_googlescholar(topic, num_results=10):
    search_query = scholarly.search_pubs(topic)
    papers = []
    for i in range(num_results):
        try:
            paper = next(search_query)
            # Validate the paper dictionary
            if (
                isinstance(paper, dict) and
                'title' in paper and
                'url' in paper and
                'author' in paper and
                'pub_year' in paper
            ):
                papers.append({
                    'title': paper['title'],
                    'authors': ', '.join(paper['author']),
                    'year': paper['pub_year'],
                    'url': paper['url']
                })
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    return papers

"""# ArXiv"""

def fetch_academic_references_arxiv(topic):
    client = Client()
    search = Search(
        query=topic,
        max_results=5,
        sort_by=SortCriterion.Relevance
    )
    references = []
    for result in client.results(search):
        references.append({
            'title': result.title,
            'author': ', '.join([author.name for author in result.authors]),
            'journal': 'arXiv',
            'year': result.published.year,
            'url': result.entry_id
        })
    return references

def get_pdf_link_arxiv(arxiv_url):
    # Extract the arXiv ID from the URL using regular expressions
    match = re.search(r'arxiv\.org/abs/(\d+\.\d+v?\d*)', arxiv_url)
    if match:
        arxiv_id = match.group(1)
        pdf_link = f'https://arxiv.org/pdf/{arxiv_id}.pdf'
        return pdf_link
    else:
        raise ValueError("ArXiv ID not found in the URL.")

def download_and_extract_text(pdf_url):
    response = requests.get(pdf_url)
    pdf_content = response.content
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

"""# Semantic Scholar"""

'''def fetch_academic_references_semanticscholar(topic, num_results=5):
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": topic,
        "limit": num_results,
        "fields": "title,authors,year,url,isOpenAccess"
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    references = []
    for result in data.get('data', []):
        if result.get('isOpenAccess'):
            authors = ', '.join([author['name'] for author in result['authors']])
            references.append({
                'title': result['title'],
                'authors': authors,
                'journal': 'Semantic Scholar',
                'year': result['year'],
                'url': result['url']
            })

    return references

def extract_semscholar_pdf_link(html):
    soup = BeautifulSoup(html_content, 'html.parser')
    pdf_link_tag = soup.find('a', {'class': 'icon-button flex-paper-actions__button alternate-sources__dropdown-button alternate-sources__dropdown-button--show-divider'})
    if pdf_link_tag:
        pdf_link = pdf_link_tag.get('href')
        return pdf_link
    else:
        print("PDF link not found.")
        return None

def fetch_pdf_link_semanticscholar(paper_url):
    # Get the HTML content of the paper URL
    response = requests.get(paper_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Extract the PDF link from the HTML content
        pdf_link = extract_semscholar_pdf_link(response.text)
        return pdf_link
    else:
        print("Failed to fetch the paper URL:", paper_url)
        return None'''

"""# PubMed"""

def fetch_academic_references_pubmed(topic, num_results=5):
    search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={topic}&retmode=json&retmax={num_results}"
    search_response = requests.get(search_url)
    search_results = search_response.json()

    papers = []

    if 'esearchresult' in search_results and 'idlist' in search_results['esearchresult']:
        paper_ids = search_results['esearchresult']['idlist']

        for paper_id in paper_ids:
            fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={paper_id}&retmode=json"
            paper_response = requests.get(fetch_url).json()

            if 'result' in paper_response and paper_id in paper_response['result']:
                paper_info = paper_response['result'][paper_id]

                # Extract authors
                authors_list = paper_info.get('authors', [])
                authors = ", ".join([author.get('name', '') for author in authors_list])

                papers.append({
                    'title': paper_info.get('title', ''),
                    'authors': authors,
                    'year': paper_info.get('pubdate', ''),
                    'url': f"https://pubmed.ncbi.nlm.nih.gov/{paper_id}/"
                })

    return papers

def fetch_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    text = ' '.join([p.get_text() for p in soup.find_all('p')])
    return text



"""# Essay Generation"""

client = OpenAI(api_key = OPENAI_API_KEY )

def summarize_texts(extracted_texts, max_length=2000):
    summarized_texts = []
    for text in extracted_texts:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                  "role": "system",
                  "content": "You are an academic assistant specialized in extracting key information from research papers. Your task is to provide concise summaries highlighting the main findings, methodology, conclusions, and any significant insights or implications."
                },
                {
                  "role": "user",
                  "content": f"Please summarize the following text, emphasizing the main findings, methodology, conclusions, and any notable insights or implications:\n\n{text}"
                }

            ],
            max_tokens=max_length,
            temperature=0.5
        )
        summary = extract_essay(response)
        summarized_texts.append(summary)
    return summarized_texts

def generate_essay_with_sources(summarized_texts, topic, max_length=3000):
    prompt = f'''Using the following summarized information, write an essay in 1000 words on {topic}, incorporating the provided summarized information:\n\n{summarized_texts}\n\n
            In your essay, address the following aspects with appropriate headdings if necessary:\n\n
            1.Introduction: Introduce the topic and provide background information.\n\n
            2.Main Body: Organize your discussion around the key points extracted from the summaries. Elaborate on each point, providing relevant details, examples, and arguments.\n\n
            3.Analysis: Critically examine the implications of the summarized information. Consider any potential limitations, controversies, or areas for further investigation.\n\n
            4.Conclusion: Summarize your main findings and arguments, highlighting the significance of the topic and suggesting potential avenues for future research.\n\n
            Ensure your essay is well-structured, coherent, and academically sound. '''
    for text in summarized_texts:
        prompt += text + "\n\n"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an academic assistant tasked with generating a university-level academic essay based on the summarized information provided."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_length,
        temperature=0.5
    )

    essay = extract_essay(response)
    return essay

def create_essay_with_academic_references_arxiv(topic):
    # Fetch references from arXiv
    references = fetch_academic_references_arxiv(topic)

    # Download and extract text from the references
    extracted_texts = []
    for ref in references:
        try:
            pdf_url = get_pdf_link_arxiv(ref['url'])
            paper_text = download_and_extract_text(pdf_url)
            extracted_texts.append(paper_text)
        except Exception as e:
            print(f"Error fetching or processing paper {ref['title']}: {e}")

    # Check if we have any extracted texts
    if not extracted_texts:
        return None, references

    # Summarize extracted texts
    summarized_texts = summarize_texts(extracted_texts)

    # Generate essay using the summarized texts
    essay = generate_essay_with_sources(summarized_texts, topic)

    return essay, references

def create_essay_with_academic_references_pubmed(topic):
    # Fetch references from arXiv
    references = fetch_academic_references_pubmed(topic)

    # Download and extract text from the references
    extracted_texts = []
    for ref in references:
        try:
            paper_text = fetch_text_from_url(ref['url'])
            extracted_texts.append(paper_text)
        except Exception as e:
            print(f"Error fetching or processing paper {ref['title']}: {e}")

    # Check if we have any extracted texts
    if not extracted_texts:
        return None, references

    # Summarize extracted texts
    summarized_texts = summarize_texts(extracted_texts)

    # Generate essay using the summarized texts
    essay = generate_essay_with_sources(summarized_texts, topic)

    return essay, references

def extract_essay(response):
    # Access the first choice from the response
    first_choice = response.choices[0]
    # Access the content of the message within the first choice
    essay_content = first_choice.message.content
    return essay_content

def generate_essay_and_references(topic, journal):
    if journal == "PUBMED":
        essay, references = create_essay_with_academic_references_pubmed(topic)
    elif journal == "ARXIV":
        essay, references = create_essay_with_academic_references_arxiv(topic)
    else:
        print("Invalid journal. Please choose 'PubMed' or 'ArXiv'.")
        return None, None

    if essay:
        print("Essay:")
        print(essay)
    else:
        print("No essay generated due to errors in fetching or processing papers.")

    print("\nReferences:")
    for ref in references:
        print(ref)

topic = input("Enter the topic: ")
journal = input("Enter the journal (PubMed or ArXiv): ").capitalize()
generate_essay_and_references(topic, journal)
