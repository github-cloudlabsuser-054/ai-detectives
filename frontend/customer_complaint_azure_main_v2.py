import streamlit as st
import openai
from constant import PROMPT_USE_LONG, PROMPT_USE_SHORT
from datetime import datetime
import pdb
import os
import time
import evaluation as eval
import pandas as pd
from openai import AzureOpenAI

# Set OpenAI API key for Azure
# openai.api_type = "azure"
# openai.api_base = "https://hsbc-aiml-team-resource.openai.azure.com/"
# openai.api_version = "2023-07-01-preview"

# openai.api_key = "c8751add6d5f406a95f91505279e33c6"

client = AzureOpenAI(
    api_key="c8751add6d5f406a95f91505279e33c6",
    azure_endpoint="https://hsbc-aiml-team-resource.openai.azure.com/",
    api_version="2023-07-01-preview"
)

st.set_page_config(
    page_title="Customer Complaint Investigation Summary Engine",
    page_icon="🔍",
    layout="wide"
)

#st.markdown(f'<style>{custom_style}</style>', unsafe_allow_html=True)

def load_documents(complaint_text):
    return [{"text": complaint_text}]

def load_file(uploaded_file):
    content = uploaded_file.read()
    cleaned_content = ' '.join(line.strip() for line in content.decode("utf-8").splitlines())
    return cleaned_content

def generate_sequence_of_events(complaint_text, short_summary_checkbox):
    user_instruction = PROMPT_USE_LONG
    complete_prompt = user_instruction + complaint_text

    if short_summary_checkbox:
        complete_prompt = PROMPT_USE_SHORT + complaint_text

    message_text = [
        {"role": "system", "content": "You are an AI assistant that helps people find information."},
        {"role": "user", "content": complete_prompt}
    ]
    
    completion = client.chat.completions.create(
        model="hsbchackthon-gpt35-turbo-16k",
        messages=message_text,
        temperature=0.1,
        max_tokens=1500,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
    )
        
    generated_text = completion.choices[0].message.content
    generated_text = generated_text.replace("Root Cause of Customer Dissatisfaction", "<span style='color:red;'>Root Cause of Customer Dissatisfaction</span>")

    return generated_text

def save_to_file(data, summary_type, output_folder="output"):
    current_directory = os.getcwd()
    #req_path="\\".join(current_directory.split("\\")[:-1])
    output_path = os.path.join(current_directory, output_folder)

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{output_path}\customer_complaint_{summary_type.lower()}_{timestamp}.txt"
    
    with open(filename, "w", encoding="utf-8") as file:
        file.write(data)

    st.success(f"File downloaded successfully! Check the '{output_folder}' folder.")  # Display success message
    return filename

# Function to inject custom CSS
def style_table_header():
    st.markdown("""
        <style>
        thead tr th { 
            font-size: 16px;.
            text-align:left;
            #color: green;  /* Your desired header text color */
            #background-color: yellow;  /* Your desired header background color */
        }
        </style>
        """, unsafe_allow_html=True)

def main():

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
                zoom: 0.58;  /* Adjust the value to control the zoom level */
            }
        </style>
        """, unsafe_allow_html=True)

    # Apply the custom style to the title
    st.markdown('<div class="title-style">Payments Investigator Autobot</div>', unsafe_allow_html=True)

    session_state = st.session_state
    if not hasattr(session_state, "summary_generated"):
        session_state.summary_generated = False
    if not hasattr(session_state, "long_summary"):
        session_state.long_summary = ""
    if not hasattr(session_state, "current_summary_type"):
        session_state.current_summary_type = ""
    if not hasattr(session_state, "similar_summary_df"):
        session_state.similar_summary_df = pd.DataFrame()
    if not hasattr(session_state, "similar_summary_df_available"):
        session_state.similar_summary_df_available = False

    complaint_text = ""
    sequence_of_events = ""

    uploaded_file = st.file_uploader("",type=["txt"])

    if uploaded_file is not None:
        file_content = load_file(uploaded_file)
        complaint_text = st.text_area("**Enter Case History:**", value=file_content, height=250)
    else:
        complaint_text = st.text_area("**Enter Case History:**", height=250, value=complaint_text)

    # Custom CSS to style the radio button label
    st.markdown("""
        <style>
        /* Style for the radio button label */
        .radio-button-label {
            font-size: 18px; /* Adjust the font size as needed */
        }
        /* Style for center-aligned content in col3 */
        .center-aligned-content {
            text-align: center; /* Center-align the content */
        }
        .left-aligned-button {
            text-align: left; /* Align button text to the left */
        }
        .generate_summary_button_style{
            font-size: 18px; /* Adjust the font size as needed */
            padding-top: 25px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Row of boxes
    col1, col2, col3 = st.columns([0.7,1,4]) # Adjust column widths as needed
    with col1:
        styled_text = f"<div class = radio-button-label>Choose Summary Type:</div>"
        st.markdown(styled_text, unsafe_allow_html=True)
    with col2:
        summary_type = st.radio("",
                                ["Long Summary", "Short Summary"],
                                horizontal=True, label_visibility="collapsed")

    similar_summary_df = pd.DataFrame()
    with col3:
        if st.button("Generate Summary"):
            with st.spinner('Processing...'):
                time.sleep(10)
    
                if complaint_text:
                    if summary_type == "Long Summary":
                        
                        sequence_of_events = generate_sequence_of_events(complaint_text, short_summary_checkbox=False)
                        session_state.long_summary = sequence_of_events
                        session_state.current_summary_type = "long_summary"

                    elif summary_type == "Short Summary":
                        
                        sequence_of_events = generate_sequence_of_events(complaint_text, short_summary_checkbox =  True)
                        session_state.current_summary_type = "Short_summary"

                    session_state.summary_generated = True
                    session_state.sequence_of_events = sequence_of_events
                    similar_summary_df = dbsearch.search_summary(session_state.sequence_of_events)
                    session_state.similar_summary_df = similar_summary_df
                    session_state.similar_summary_df_available = True
    #print(session_state.similar_summary_df.size)
    custom_text_area_style = """
        border-radius: 1px;
        margin-top: 10px;
        margin-bottom: 10px;
        margin-right: 15px;
        margin-left: 8px;
        background-color: #F0FFFF;
        padding-top: 10px;
        padding-right: 10px;
        padding-bottom: 10px;
        padding-left: 10px;
    """
    #print("pre",len(sequence_of_events))
    sequence_of_events = sequence_of_events.strip()
    #print("post",len(sequence_of_events))
    eval_table = None
    #if len(sequence_of_events) > 0:
    #    eval_table = eval.get_eval_table(complaint_text,sequence_of_events)
    #styled_eval_table = eval_table.style.apply(highlight_max, axis=1)

    #-------------------------------------------
    # Define your custom styles in a <style> tag
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
        }

        .stTabs [aria-selected="true"] {
            background-color: #FFFFFF;
        }
        

    </style>
    """
    # Inject custom CSS with markdown
    st.markdown(custom_css, unsafe_allow_html=True)
    tab1, tab2, tab3  = st.tabs(["Summary", "Summary Evaluation","Similar Cases"])

    with tab1:
        # Row of boxes
        styled_text = f"<div style='background-color:#F0FFFF; padding:20px; overflow-y: scroll; height: 250px; width:100%'><div><strong>Customer Complaint Summary:</strong><br></div>{sequence_of_events}</div>"
        st.markdown(styled_text, unsafe_allow_html=True)        

    with tab2:
        if len(sequence_of_events) > 0:
            #time.sleep(60)
            eval_table = eval.get_eval_table(complaint_text,sequence_of_events)
            eval_table_str = eval_table.to_html().replace("&lt;li&gt;", "<li>").replace("&lt;/li&gt;","</li>").replace("\\n","").replace("\\n","")
            #.replace("&lt;li&gt;", "<li>").replace("&lt;/li&gt;","</li>").replace("\n","<br>").replace("\n","").replace("<\li>","")
            #print(eval_table_str)
            styled_text = f"<div style='background-color:#F0FFFF; padding:20px; overflow-y: scroll; height: 250px; width:100%'><div><strong>Summary Evaluation:</strong><br></div>{eval_table_str.strip()}</div>"
            st.markdown(styled_text, unsafe_allow_html=True)
            #st.markdown(f'<div style="{custom_text_area_style}"><strong>Summary Evaluation:</strong><br>{eval_table_str.strip()}</div>',unsafe_allow_html=True)

    with tab3:
        #style_table_header()
        #styled_text = f"<div style='background-color:#F0FFFF; padding:20px; overflow-y: scroll; height: 100px; width:100%'><div><strong>Similar Summeries:</strong><br></div>{st.table(session_state.similar_summary_df)}</div>"
        with st.container():
            st.table(session_state.similar_summary_df)
            #st.markdown(styled_text, unsafe_allow_html=True)
    if session_state.similar_summary_df_available:
        st.success('Done!')
    col3, col4 = st.columns([0.5,5])
    
    if session_state.summary_generated:
        with col3:
            if st.button("Download Summary", help="Click to download the generated summary"):
                save_to_file(session_state.sequence_of_events, session_state.current_summary_type)

        with col4:
            if st.button("Clear"):
                complaint_text = ""
                sequence_of_events = ""   
    
if __name__ == "__main__":
        main()
