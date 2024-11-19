import time
from google.cloud import bigquery
import streamlit as st
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Part, Tool
import pandas as pd
import numpy as np
import prompttemp
import re
from util import *
import requests
import folium
from streamlit_folium import folium_static
import math
import os
from sklearn.cluster import KMeans
from random import random
import plotly.graph_objs as go
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score
import ast
import itertools



generation_config = {
    "max_output_tokens": 2000,
    "temperature": 0
 
}
safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_NONE
    ),
]
model = GenerativeModel(
    "gemini-pro-experimental",
    generation_config=generation_config,safety_settings=safety_settings
    
)
st.set_page_config(
    page_title="Supplier Forensics Agent",
    page_icon="images/AAM_Logo.jpeg",
    layout="wide",
)

col1, col2 = st.columns([8, 1])
with col1:
    st.title("Supplier Forensics Agent using Gemini")
with col2:
    st.image("images/AAM_Logo.jpeg")

st.subheader("Natural Language Query to SQL, Powered by in Gemini")


api_requests_and_responses=[]
backend_details=""
## Folium v2

# API KEY

if os.path.isfile("credentials.py"):
    import credentials
    google_API_KEY = credentials.google_API_KEY
else:
    google_API_KEY = st.secrets["google_API_KEY"]


def create_map():
    # Create the map with Google Maps
    map_obj = folium.Map(tiles=None)
    folium.TileLayer("https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", 
                     attr="google", 
                     name="Google Maps", 
                     overlay=True, 
                     control=True, 
                     subdomains=["mt0", "mt1", "mt2", "mt3"]).add_to(map_obj)
    return map_obj

def add_markers(map_obj, locations, popup_list=None):
    if popup_list is  None:
        # Add markers for each location in the DataFrame
        for lat, lon in locations:
            folium.Marker([lat, lon]).add_to(map_obj)
    else:
        for i in range(len(locations)):
            lat, lon = locations[i]
            popup = popup_list[i]
            folium.Marker([lat, lon], popup=popup).add_to(map_obj)

    # Fit the map bounds to include all markers
    south_west = [min(lat for lat, _ in locations) - 0.02, min(lon for _, lon in locations) - 0.02]
    north_east = [max(lat for lat, _ in locations) + 0.02, max(lon for _, lon in locations) + 0.02]
    map_bounds = [south_west, north_east]
    map_obj.fit_bounds(map_bounds)

    return map_obj




#####

def drawmap(prompt,chat):
    try:
        lat_lng_list=[]
        api_response, api_response_df,query=queryresponse(prompt,chat)
        summary_prompt= "Please summarize the results  " + api_response_df.to_string() + "give a concise, high-level summary in content with dataset schema " + str(prompttemp.json_data)
        response = chat.send_message(summary_prompt)
        #response = response.candidates[0].content.parts[0].text
        response = response.text
        st.markdown(response)
        with st.expander("Show Map:"):
                        chart_data = api_response_df
                        #st.dataframe(chart_data)
                        #st.map(chart_data,latitude='lat',longitude='long',use_container_width=True)
                        ##folium
                        m = create_map()
                        #lat_lng_list.append((chart_data['vendor_name'],(chart_data['lat'], chart_data['long'])))
                        for index, row in chart_data.iterrows():
                            vendor_name = row['vendor_name']
                            lat = row['lat']
                            long = row['long']
                            lat_lng_list.append((vendor_name, (lat, long))) 
                            
                        df = pd.DataFrame(lat_lng_list, columns=["vendor_name", "lat_lng"])

                        m = add_markers(m, df['lat_lng'], df['vendor_name'])
                        # folium.Circle(location=middle, radius=r, color='red', fill_color='red', fill_opacity=0.1).add_to(m)
                        folium_static(m)
                                    

        with st.expander("Show Query:"):
                        st.write(f"Query {query}  Response {api_response}")
        
        api_requests_and_responses.append(
                                ["map", query, api_response]
                            )
        return response
    except Exception as e: 
        response= "Please try again"
        return response
        
def drawchart(prompt,chat):
    
    try:
        api_response, api_response_df,query=queryresponse(prompt,chat)
        summary_prompt= "Please summarize the results  " + api_response + "give a concise, high-level summary in content with dataset  schema " + str(prompttemp.json_data)
        response = chat.send_message(summary_prompt)

        #response = response.candidates[0].content.parts[0].text
        response = response.text
        st.markdown(response)
        with st.expander("Show Graph:"):
                    chart_data = api_response_df
                    #st.dataframe(chart_data,hide_index=True )
                    edited_df = st.data_editor(chart_data,hide_index="True") # 👈 An editable dataframe
                    st.bar_chart(edited_df ,use_container_width=True,stack=False)
                    
        with st.expander("Show Query:"):
                        st.write(f"Query {query}  Response {api_response}")
        
        api_requests_and_responses.append(
                                ["chart", query, api_response]
                            )
        return response
    except: 
        return "Please try again"
            
def drawtable(prompt,chat):
    try:
        api_response, api_response_df,query=queryresponse(prompt,chat)
        summary_prompt= "Please summarize the results  " + api_response + "give a concise, high-level summary in content with dataset  schema " + str(prompttemp.json_data)

        response = chat.send_message(summary_prompt)

        #response = response.candidates[0].content.parts[0].text
        response= response.text
        st.markdown(response)
        with st.expander("Show table:"):
                    table_data = api_response_df
                    st.dataframe(table_data,use_container_width=True)
        with st.expander("Show Query:"):
                        st.write(f"Query {query}  Response {api_response}")
        api_requests_and_responses.append(
                                ["table", query,api_response]
                            )
        return response
    except: 
        return "Please try again"
    
def drawimage(prompt,chat):
    try:
        api_response, api_response_df,query=queryresponse(prompt,chat)
        summary_prompt= "Please summarize the results  " + api_response + "give a concise, high-level summary in content with dataset  schema " + str(prompttemp.json_data)

        response = chat.send_message(summary_prompt)

        #response = response.candidates[0].content.parts[0].text
        response= response.text
        st.markdown(response)
        with st.expander("Show table:"):
                    table_data = api_response_df
                    image_data= table_data[['purchase_order', 'vendor_name', 'part_number', 'part_image']]
                    st.data_editor ( image_data,
                    column_config={
                        "part_image": st.column_config.ImageColumn(
                            label="Part Image", width= "large",help=None
                        )
                    },
                    hide_index=True,
                    )
                    
                    #st.dataframe(table_data,use_container_width=True)
        with st.expander("Show Query:"):
                        st.write(f"Query {query}  Response {api_response}")
        api_requests_and_responses.append(
                                ["table", query,api_response]
                            )
        return response
    except Exception as e: 
        return "Please try again"
    



def generalresponse(prompt,chat):
    prompt =  f"Hello I am a  Supplier Forensics Agent I can answer questions based on Vendor performace using schema   {str(json_data)} question is : {prompt} " 
    response =model.generate_content(prompt)
    st.write (response.text)
    return response

def drawqueryoutput(prompt,chat):
    try:
        api_response, api_response_df,query=queryresponse(prompt,chat)
        summary_prompt= "Please summarize the results  " + api_response + "give a concise, high-level summary in content with dataset  schema " + str(prompttemp.json_data)

        response = chat.send_message(summary_prompt)

        #response = response.candidates[0].content.parts[0].text
        response = response.text
        st.markdown(response)
        with st.expander("Show Query:"):
                        st.markdown(f"Query {query}  \n Response {api_response}")
        api_requests_and_responses.append(
                                ["query", query,api_response]
                            )
        return response
       
    except Exception as e: 
            return "Please try again"
        
with st.expander("Sample Questions", expanded=True):
    

    st.write(
        """
        - How units of part BD001 were ordered in the month of January 2022?
        - What was Best Door Company overall defect rate from vendor purchase order for the month of February 2022?
        - What is the year to date defect rate starting from jan 2022 from vendor purchase order of Part BD002?
        - How many units of AG001 were ordered in March 2022?
        - /map Show me locations of all my vendors
        - /table Show me vendor name and locations of all my vendors
        - /chart monthly receipt of good and defected items for part number BD001 in year 2022. return result in column month, total_ok and total_defective
        - Show me a CAPA incident record where Part BD001 had a Dent defect
        - How CAPA incidents does Part BD001 have in the CAPA log?
        - Does  Part BD001 have both incoming quality defect and CAPA incidents on the same day?
        - Recommend alternative vendor for Clarkston Window & Door who sells BD001 
        - Recommend alternatives for part BD001 and list vendors who sell it
        - /map Recommend alternatives for part BD001 and list vendors who sell it also give locations
        - /image show me purchase orders for part number BD001 that has defect 'Dent' and contains part image




    """
    )
    # st.write(
    #     """
    #     - How units of part BD001 were ordered in the month of January 2022?
    #     - What was Best Door Company overall defect rate from vendor purchase order for the month of February 2022?
    #     - What is the YTD defect rate starting from jan 2022 from vendor purchase order of Part BD002?
    #     - How many units of AG001 were ordered in March 2022?
    #     - For part BD001 draw a bar graph of monthly receipts and defects for 2022 in vendor purchase order table? Monthly buckets on X axis and QTY in Y axis. Each month with two bars (QTY OK and QTY Defective) [Shows Graph]
    #     - Show me locations of all my vendors [Shows Map]

    # """
    # )

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"].replace("$", "\$"))  # noqa: W605
        try:
            with st.expander("Function calls, parameters, and responses"):
                st.markdown(message["backend_details"])
        except KeyError:
            pass


if prompt := st.chat_input("Ask me about supplier forensics..."):
    try:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Getting Supplier Forensic data..."):
                message_placeholder = st.empty()
                full_response = ""
                chat = model.start_chat(response_validation=False)
                intent,clearprompt=extract_intent(prompt)
                if intent=="/map":
                    full_response= drawmap(clearprompt,chat)
                elif intent=="/chart":
                    full_response=drawchart(clearprompt,chat)
                elif intent=="/table":
                    full_response=drawtable(clearprompt,chat) 
                elif intent=="/image":
                    full_response=drawimage(clearprompt,chat) 
                else:
                    full_response=drawqueryoutput(clearprompt,chat)

        
            backend_details += (
                "   - Action ```"
                + str(api_requests_and_responses[-1][0])
                + "```"
            )
            backend_details += "\n\n"
            backend_details += (
                "   - Query ```"
                + str(api_requests_and_responses[-1][1])
                + "```"
            )
            backend_details += "\n\n"
            backend_details += (
                "   - response ```"
                + str(api_requests_and_responses[-1][2])
                + "```"
            )
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response,
                    "backend_details": backend_details,

                    
                }
            )
    except Exception as e:
        st.write ("")



