
import base64
from io import BytesIO
import streamlit as st
import numpy as np
from vertexai.preview.vision_models import Image, ImageGenerationModel
from itertools import cycle
from tempfile import NamedTemporaryFile
import os
from google.cloud import storage
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Part, Tool,GenerationConfig,SafetySetting
from streamlit_image_select import image_select
from PIL import Image
from util import *
from prompttemp import *

model = GenerativeModel(
    "gemini-pro-experimental",
    generation_config={"temperature": 0},
  
)

st.set_page_config(
    page_title="Multimodal Based Supplier Forensics",
    page_icon="images/AAM_Logo.jpeg",
    layout="wide",
)


generation_config = {
    "max_output_tokens": 1000,
    "temperature": 0.2,
    "top_p": 0.95,
}
col1, col2 = st.columns([8, 1])
with col1:
    st.title("Multimodal Based Supplier Forensics")
with col2:
    st.image("images/AAM_Logo.jpeg")
    




gcloud_bucket_name = "gemvendordemo"
storage_client = storage.Client()
bucket = storage_client.get_bucket(gcloud_bucket_name)


detailed_analysis=""
defect_detail=""
defect_cateogy=""

option = st.selectbox(
    "Modality",
    ("Image", "Video"),
)

if option=="Image":
    
    uploadimage = st.file_uploader("Upload Image",type=['png','jpg','jpeg'])
    if uploadimage:
        st.image(uploadimage,use_column_width=True)
    else:
        ResetSession()
        
    query=st.text_input("Please enter your query")
    st.write("**Sample Queries**")
    st.write("- How many other incoming quality records contain this same defect classification?")
    st.write("- What is percentage of the total defects for the month of Jan 2022 where this defect classification?")

    submitted=st.button("Submit")

    if submitted and uploadimage is not None:
        with st.spinner("Analyzing Image file......"):
            if 'defect_cateogy' not in st.session_state:
                detailed_analysis,defect_detail,defect_cateogy=Image_analysis(uploadimage)
                st.session_state['defect_cateogy'] = defect_cateogy
                st.session_state['defect_detail'] = defect_detail
                st.session_state['detailed_analysis'] = detailed_analysis
                
    
else:
    video_url=""
    uploadvideo = st.file_uploader("Upload Video",type=['mp4'])
    if uploadvideo is not None:
        if not file_exists(uploadvideo.name):
            with NamedTemporaryFile(dir='.', suffix='.mp4') as f:
                f.write(uploadvideo.getbuffer())
                public_url=upload_blob(f.name, uploadvideo.name)
        
            st.write("Original Video")
            st.video(public_url)
            video_url=public_url
            #results = video_analysis(public_url)
        
        else:
            st.write("Original Video")
            st.video("https://storage.googleapis.com/gemvendordemo/" +uploadvideo.name)
            #results = video_analysis("gs://gemvendordemo/" +uploadvideo.name)
            video_url="gs://gemvendordemo/" +uploadvideo.name
    else:
        ResetSession()
                
    query=st.text_input("Please enter your query")
    st.write("**Sample Queries**")
    st.write("- How many other incoming quality CAPA records contain this same defect classification?")
    st.write("- What is percentage of the total defects for the month of Jan 2022 where this defect classification?")
    defect_cateogy=""
    submitted=st.button("Submit")
    
    if submitted and uploadvideo is not None:
        with st.spinner("Analyzing Video file..."):
            if 'defect_cateogy' not in st.session_state:
                detailed_analysis,defect_detail,defect_cateogy=video_analysis(video_url)
                st.session_state['defect_cateogy'] = defect_cateogy
                st.session_state['defect_detail'] = defect_detail
                st.session_state['detailed_analysis'] = detailed_analysis

  
with st.expander("**Defect Category**", expanded=True):
    try:
        if 'defect_cateogy' in st.session_state:

            defect_cateogy=st.session_state['defect_cateogy']
            defect_detail=st.session_state['defect_detail']
            detailed_analysis=st.session_state['detailed_analysis']
            
            st.write(f"**{defect_cateogy}**")
            st.write(f"**{query}**")
            
            prompt=f"{query} :  + {defect_cateogy} ?"
            with st.spinner("Getting Supplier Forensic data..."):

                intent,clearprompt=extract_intent(prompt)
                chat = model.start_chat(response_validation=False)
                api_response, api_response_df,query=queryresponse(prompt,chat)
                summary_prompt= "Please summarize the results  " + api_response + "give a concise, high-level summary in content with dataset  schema " + str(json_data)
                response = chat.send_message(summary_prompt)
                response = response.candidates[0].content.parts[0].text
                st.write(response)
                st.write("**Query**")
                st.write(query)
            
    except Exception as e:
        print("hello")
        
with st.expander("**Defect Detail**", expanded=False):
    if 'defect_detail' in st.session_state:
        st.write(defect_detail)
    
with st.expander("**Detailed Analysis**", expanded=False):
     if 'detailed_analysis' in st.session_state:
        st.write(detailed_analysis)
    


  
  
  

#batteryfaultimg = bucket.get_blob('gs://gemvendordemo/batteryfault.jpeg')  # use get_blob to fix generation number, so we don't get corruption if blob is overwritten while we read it.

# import streamlit as st
# from st_click_detector import click_detector

# content = """
#     <a href='#' id='Image 1'><img width='20%' src='https://storage.googleapis.com/gemvendordemo/batteryfault.jpeg'></a>
#     <a href='#' id='Image 2'><img width='20%' src='https://storage.googleapis.com/gemvendordemo/alternator.jpeg'></a>
#     <a href='#' id='Image 3'><img width='20%' src=' https://storage.googleapis.com/gemvendordemo/tire.jpg'></a>
#     <a href='#' id='Image 4'><img width='20%' src=' https://storage.googleapis.com/gemvendordemo/breakpad.jpeg'></a>

#     """
# clicked = click_detector(content)
# image_gs=""
# if clicked == 'Image 1':
#     image_gs='gs://gemvendordemo/batteryfault.jpeg'
# elif clicked== 'Image 2':
#     image_gs='gs://gemvendordemo/alternator.jpeg'
# elif clicked== 'Image 3':
#     image_gs='gs://gemvendordemo/tire.jpg'
# elif clicked== 'Image 4':
#     image_gs='gs://gemvendordemo/breakpad.jpeg'
# else:
#     st.write ('Please select image for analysis')

# if image_gs!="" : 
#    with st.spinner("Generating..."):
#         ingredients=analyse_defects(image_gs)
