import streamlit as st
import hashlib
import time
from langchain.chains.summarize import LLMChain, MapReduceDocumentsChain, ReduceDocumentsChain,StuffDocumentsChain
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from blob import getDocuments, getblobdirs, deleteblobdir, clearblob
from constant import map_template, reduce_template, fraud_resolution
from evaluation import get_eval_table
from datetime import datetime
import dotenv
import os
from openai import AzureOpenAI

envpath = os.path.join(os.getcwd(),".env")
dotenv.load_dotenv(envpath)

client = AzureOpenAI(
  azure_endpoint = "https://aidetectives.openai.azure.com/", 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version="2024-02-15-preview"
)

llm = AzureChatOpenAI(
        azure_deployment="ai-detectives-gpt316k",  
        temperature=0.1,
        max_tokens=5000,
        model_kwargs={
        "top_p":0.95,
        "frequency_penalty":0,
        "presence_penalty":0,
        "stop":None}
        )

def getStuffSummary(docs):
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = LLMChain(llm=llm, prompt=map_prompt)
    combine_documents_chain = StuffDocumentsChain(
        llm_chain=map_chain, document_variable_name="docs"
    )
    result = combine_documents_chain.invoke(docs)
    output_parser = StrOutputParser()
    return output_parser.parse(result['output_text'])

def getSummary(docs):
    
    map_prompt = PromptTemplate.from_template(map_template)

    map_chain = LLMChain(llm=llm, prompt=map_prompt)


    reduce_prompt = PromptTemplate.from_template(reduce_template)


    # Run chain
    reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)

    # Takes a list of documents, combines them into a single string, and passes this to an LLMChain
    combine_documents_chain = StuffDocumentsChain(
        llm_chain=reduce_chain, document_variable_name="docs"
    )

    # Combines and iteratively reduces the mapped documents
    reduce_documents_chain = ReduceDocumentsChain(
        # This is final chain that is called.
        combine_documents_chain=combine_documents_chain,
        # If documents exceed context for `StuffDocumentsChain`
        collapse_documents_chain=combine_documents_chain,
        # The maximum number of tokens to group documents into.
        token_max=4000,
    )


    # Combining documents by mapping a chain over them, then combining results
    map_reduce_chain = MapReduceDocumentsChain(
        # Map chain
        llm_chain=map_chain,
        # Reduce chain
        reduce_documents_chain=reduce_documents_chain,
        # The variable name in the llm_chain to put the documents in
        document_variable_name="docs",
        # Return the results of the map steps in the output
        return_intermediate_steps=False,
    )

    result = map_reduce_chain.invoke(docs)
    output_parser = StrOutputParser()
    return output_parser.parse(result['output_text'])


def getResolution(summary):

    resolution_prompt= PromptTemplate.from_template(fraud_resolution)
    output_parser = StrOutputParser()
    chain = resolution_prompt | llm | output_parser
    result = chain.invoke({"summary":summary})
    return result

st.set_page_config(
    page_title="Fraud detection",
    page_icon="⚠️",
    layout="wide"
)

def load_text_file(file):
  """Loads a text file and returns its contents."""
  with open(file, "r") as f:
    return f.read().decode("utf-8")
  
def click_button():
    st.session_state.clicked = True

def save_to_file(summary, resolution, output_folder="output"):
    current_directory = os.getcwd()
    #req_path="\\".join(current_directory.split("\\")[:-1])
    output_path = os.path.join(current_directory, output_folder)

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{output_path}\Summary_{timestamp}.txt"
    
    with open(filename, "w", encoding="utf-8") as file:
        file.write(summary)
        file.write(resolution)

    st.success(f"File downloaded successfully! Check the '{output_folder}' folder.")  # Display success message
    return filename


def main(): 
     
    session_state = st.session_state
    if not hasattr(session_state, "summary_generated"):
        session_state.summary_generated = False
    if not hasattr(session_state, "resolution_generated"):
        session_state.resolution_generated = False
    if not hasattr(session_state, "summary"):
        session_state.summary = ""
    if not hasattr(session_state, "resolution"):
        session_state.resolution = ""
    if not hasattr(session_state, "docs"):
        session_state.docs = []
    if not hasattr(session_state, "uploaded_file"):    
        session_state.uploaded_files = []
    if 'clicked' not in st.session_state:
        session_state.clicked = False

    
        # Custom CSS to center the title
    st.markdown("""
        <style>
        .title-style {
            font-size: 40px;
            font-weight: bold;
            text-align: center;
            margin: -70px;
            border; -30px;
            padding: -30px;  
        }
        body {
                zoom: 1;  /* Adjust the value to control the zoom level */
            }
        </style>
        """, unsafe_allow_html=True)

    # Apply the custom style to the title
    st.markdown('<div class="title-style">detective.ai</div>', unsafe_allow_html=True)

    with st.form("my-form", clear_on_submit=True):
        uploaded_files = st.file_uploader("Choose multiple text files", accept_multiple_files=True, type=['txt'])
        submitted = st.form_submit_button("submit")
        if submitted:
            session_state.uploaded_files = uploaded_files
            session_state.docs = getDocuments(uploaded_files=uploaded_files)
        
    # Allow the user to upload multiple files
    # uploaded_files = st.file_uploader("Choose multiple text files", accept_multiple_files=True, type=['txt'])
 
    for doc in session_state.docs:
        st.write(f"**Document: {os.path.basename(doc.metadata['source'])}**")
        st.text_area(label="", value=doc.page_content, height=200)
    
    # if st.button("Clear File Uploader"):
    #     st.session_state.uploaded_file = None
    #     session_state.docs = []
    #     st.experimental_rerun()

    if st.button("Clear"):
        with st.spinner('Processing...'):
         if clearblob():
            st.warning('all emails deleted!!', icon="⚠️")
            session_state.uploaded_file = None
            session_state.summary = ""
            session_state.summary_generated = False
            session_state.resolution = ""
            session_state.docs=[]
            st.rerun()

    # List of directories from Blob container (replace this with your actual list)
    directories = getblobdirs()

    # Display the list of directory elements with buttons
    for directory in directories:
        display_directory_element(directory)

    if st.button("Generate Summary", on_click=click_button):
        with st.spinner('Processing...'):
            if st.session_state.clicked:
                if session_state.docs:
                    # session_state.summary = getSummary(session_state.docs)
                    session_state.summary = getStuffSummary(session_state.docs)
                    session_state.summary_generated = True
                    session_state.resolution = getResolution(session_state.summary)
                    session_state.clicked = False
        
    custom_css = """
    <style>
        button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
        font-size: 20px;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #F0F2F6;
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
            padding: 10px;
            margin 10px;
        }

        .stTabs [aria-selected="true"] {
            background-color: #FFFFFF;
        }
        

    </style>
    """
    # Inject custom CSS with markdown
    st.markdown(custom_css, unsafe_allow_html=True)
    tab1, tab2, tab3= st.tabs(["Summary", "Resolution","Summary Evaluation"])

    with tab1:
        # Row of boxes
        styled_text = f"<div style='background-color:#F0FFFF; padding:20px; margin : 10 px; overflow-y: scroll; height: 250px; width:100%'><div><strong>Summary:</strong><br></div>{session_state.summary}</div>"
        st.markdown(styled_text, unsafe_allow_html=True)        

    with tab2:
        styled_text = f"<div style='background-color:#F0FFFA; padding:20px; margin : 10 px; overflow-y: scroll; height: 250px; width:100%'><div><strong>Resolution:</strong><br></div>{session_state.resolution}</div>"
        st.markdown(styled_text, unsafe_allow_html=True)
    with tab3:
         if len(session_state.summary) > 0:
            
            eval_table = get_eval_table(session_state.docs, session_state.summary)
            eval_table_str = eval_table.to_html().replace("&lt;li&gt;", "<li>").replace("&lt;/li&gt;","</li>").replace("\\n","").replace("\\n","")
            styled_text = f"<div style='background-color:#fdf0ff; padding:20px; margin : 10 px; overflow-y: scroll; height: 250px; width:100%'><div><strong>Summary Evaluation:</strong><br></div>{eval_table_str.strip()}</div>"
            st.markdown(styled_text, unsafe_allow_html=True)
    
    col1, col2 = st.columns([0.7,1])
    
    if len(session_state.summary) > 0:
        with col1:
            if st.button("Download Summary", help="Click to download the generated summary"):
                save_to_file(session_state.summary, session_state.resolution)

        with col2:
            pass
            # if st.button("Clear"):
            #     session_state.summary = ""
            #     session_state.summary_generated = False
            #     session_state.resolution = ""
            #     st.rerun()


if __name__ == "__main__":
    main()




# Define a function to display the directory element with buttons
def display_directory_element(directory_name):
    st.write(f"Directory: {directory_name}")
    
    # Button to delete the directory
    if st.button(f"Delete {directory_name}"):
        # Add code here to delete the directory
        st.write(f"Directory {directory_name} deleted.")
    
    # Button for custom action
    if st.button(f"Custom Action for {directory_name}"):
        # Add your custom action code here
        st.write(f"Custom action performed for {directory_name}.")
