import requests
import json
from typing import Dict

import streamlit as st
from annotated_text import annotated_text

BACKEND_IP = 'http://127.0.0.1:5000'

@st.cache_data(show_spinner=False)
def request_answers(data):
    response = requests.post(
        f'{BACKEND_IP}/query', 
        data=data,
    )
    return response.json()

@st.cache_data(show_spinner=False)
def request_docstore_stats():
    response = requests.get(
        f'{BACKEND_IP}/docstorestats', 
    )
    return response.json()


def display_annotated_context(answer, context):
    idx = context.find(answer)
    idx_end = idx + len(answer)

    annotated_text(
        context[:idx], 
        (answer, "", "#376c39"), 
        context[idx_end:]
    )


def _get_document(documents, document_id):
    for document in documents:
        if document['id'] == document_id:
            return document['content']
        

def display_annotated_text_with_offset(document, offsets: Dict[str, int]):
    start, end = offsets['start'], offsets['end']
    color = "#376c39"

    annotated_text(    
        document[:start], 
        (document[start:end], "", color), 
        document[end:]
    )


def run_query(data, question):
    if question:
        with st.spinner(text=':crown: Looking for answers...'):
            response = request_answers(data)

            if not response['answers']:
                # TODO: `display could not find answers``
                return 
            
            use_long_contexts = st.sidebar.checkbox('Display long contexts')
                
            generate_answers(
                response, 
                alternatives=False, 
                use_long_contexts=use_long_contexts
            )

            if st.sidebar.checkbox('Show alternative answers'):
                st.write("### Alternatives")
                generate_answers(
                    response, 
                    alternatives=True, 
                    use_long_contexts=use_long_contexts
                )
            #st.button(
            #    'Alternatives', 
            #    on_click=generate_answers, 
            #    args=(response,),
            #    kwargs={'alternatives': True}
            #)
            

        #if st.sidebar.checkbox('Show debug info'):
        #    st.subheader('REST API JSON response')
        #    st.write(response)


def generate_answers(response, alternatives=False, use_long_contexts=False):
    # TODO: add an example of the expected response (an example of the haystack run output) 
    
    answer_entries = (
        [response['answers'][0]]
        if not alternatives 
        else response['answers'][1:]
    )

    for answer_entry in answer_entries:
        answer = answer_entry['answer']

        if not answer:
            # TODO: do something about answer being empty string
            st.write('Best answer cannot be found among the documents, finding best alternative...')
            continue

        offsets = answer_entry['offsets_in_document'][0]
        
        document_id = answer_entry['document_id'] if 'document_id' in answer_entry else answer_entry['document_ids'][0]
        document = _get_document(response['documents'], document_id)
        
        if len(document) < 1000 or use_long_contexts:
            display_annotated_text_with_offset(document, offsets)
        else:
            context = '...' + answer_entry['context'] + '...'
            display_annotated_context(answer, context)
            

        document_name = answer_entry['meta']['name'] if 'meta' in answer_entry and 'name' in answer_entry['meta'] else 'Unknown'            
        st.write(f"**Score**: {answer_entry['score'] * 100:.1f}   **Source**: {document_id}")
        
    st.write(f"Retrieved {len(answer_entries)} answers in {response['runtime']:.1f} s.")


st.set_page_config(
     page_title="Haystack - Ask me something and get an answer!",
     page_icon=":crown:",
     layout="centered",
     initial_sidebar_state="auto",
)

st.title(':question: OpenQA pipeline demo app')

docstore_stats = request_docstore_stats()
doc_count = f"{docstore_stats['document_count']:,}"
st.subheader(f"Ask me something and get an answer\n(Nbr. of documents available: {doc_count.replace(',', ' ')})")

question = st.text_input('')

data = json.dumps(
    {
        'query': question,
    }
)

run_query(data, question)

