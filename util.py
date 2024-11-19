from google.cloud import bigquery
import streamlit as st
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Part, Tool,SafetySetting
import pandas as pd
import numpy as np
from prompttemp import *
import re
from google.cloud import storage
from tempfile import NamedTemporaryFile
import os


generation_config = {
    "max_output_tokens": 4000,
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
)




gcloud_bucket_name = "gemvendordemo"
storage_client = storage.Client()
bucket = storage_client.get_bucket(gcloud_bucket_name)


def extract_intent(prompt):
    try: 
        patterns = ["/map", "/chart", "/table", "/image"]
        potential_matches = [re.search(pattern, prompt) for pattern in patterns]
        match = any(potential_matches)  # Check if any match object exists
        if match:
            # Iterate through potential_matches to find the first successful match
            for potential_match in potential_matches:
                if potential_match:  # Check if this specific match object is not None
                    intent = potential_match.group(0)  # Extract the matched pattern
                    split_result = re.split(intent, prompt, maxsplit=1)
                    if len(split_result) > 1:
                        return intent, split_result[1].strip()  # Remove leading/trailing whitespace
                    else:
                        return intent, prompt

            
        else:
            intent=""
            return intent,prompt  # Or a different descriptive value for no match
    except: 
        intent=""
        return intent,prompt 

def cleanresponse(output):
    cleaned_response = (
                            output
                            .replace("sql","")
                            .replace("\\n", "")
                            .replace("\n", "")
                            .replace("\\", "")
                            .replace("`", "")
                            .replace("``", "")
                        )
    return cleaned_response.strip()
def queryresponse(prompt,chat):
    prompt = "generate big query SQL statement to for following questions: " + prompt + " use the following big query data structure and schema : " + str(json_data)  
    #st.write(prompt)
    try:
        client = bigquery.Client()
        response = chat.send_message(prompt)
        #st.write(response.text)

        #response = response.candidates[0].content.parts[0]
        #print(response.text)
        
        job_config = bigquery.QueryJobConfig(
                        maximum_bytes_billed=100000000
                    )  # Data lim       
        
        query=response.text 
        cleaned_query = (
                            query
                            .replace("sql","")
                            .replace("\\n", " ")
                            .replace("\n", " ")
                            .replace("\\", " ")
                            .replace("`", " ")
                            .replace("``", " ")
                        )
        #print (cleaned_query)
        #st.write (cleaned_query)
        
        query_job = client.query(cleaned_query, job_config=job_config)
        api_response_df = query_job.result().to_dataframe()

        api_response = list(query_job.result())
        api_response = str([dict(row) for row in api_response])
        api_response = api_response.replace("\\", "").replace("\n", "")
        # api_requests_and_responses.append(
        #                     ["Query", cleaned_query, api_response]
        #                 )
        return api_response, api_response_df,cleaned_query
    except  Exception as e:
        try:
            response = chat.send_message(prompt)
           # response = response.candidates[0].content.parts[0]
        
            job_config = bigquery.QueryJobConfig(
                            maximum_bytes_billed=100000000
                        )  # Data lim       
            
            query=response.text 
            cleaned_query = (
                                query
                                .replace("sql","")
                                .replace("\\n", " ")
                                .replace("\n", " ")
                                .replace("\\", " ")
                                .replace("`", " ")
                                .replace("``", " ")
                            )
            query_job = client.query(cleaned_query, job_config=job_config)
            api_response = query_job.result()
            api_response_df = query_job.result().to_dataframe()
            api_response = str([dict(row) for row in api_response])
            api_response = api_response.replace("\\", "").replace("\n", "")
            # api_requests_and_responses.append(
            #                 ["Query", cleaned_query,api_response]
            #             )
            return api_response, api_response_df,query
        except Exception as e: 
            st.write ("Please try again")
            api_response="please try again"
            api_response_df=pd.DataFrame()
            return api_response, api_response_df,query



def analyse_defects(file_url,type):

    # prompt = """Analyze the attached image of an automobile part. 

    #         Provide concise details about any visible defects, including:
    #         * **Defect type:** Briefly describe the nature of the defect (e.g., crack, corrosion, deformation).
    #         * **Location:** Specify where the defect is situated on the part (e.g., edge, surface, connection point).
    #         * **Severity (optional):** If possible, estimate the severity of the defect (e.g., minor, major, critical).

    #         Please keep your response brief and focused on the most relevant information.

    #          Cut, Dent, Leak,  Wiring, Scratch , Fastener, Alignment"""
    try: 
    
        if type=="Image":
            prompt="""**Image Analysis Request** Please meticulously examine the provided image of the automotive part and furnish a detailed defect analysis. **Essential Information:** * **Image:** [Provide a clear and well-lit image of the automotive part] * **Part Name:** [Specify the exact name or type of the automotive part] **Analysis Requirements:** 1. **Defect Identification:** * Clearly pinpoint and describe any visible defects in the image. * Specify the precise location of each defect on the part. * If multiple defects are present, enumerate and describe each one separately. 2. **Severity Assessment:** * Evaluate the severity of each identified defect on a scale of: * **Critical**: Poses an immediate safety risk or renders the part inoperable * **Major**: Significantly impacts functionality or longevity * **Minor**: Has a negligible impact on performance but may worsen over time * Provide a brief justification for each severity assessment. 3. **Root Cause Hypothesis:** * Propose potential causes for each defect, considering factors such as: * Manufacturing flaws * Material fatigue or wear and tear * Improper installation or maintenance * Environmental damage * Impact or stress 4. **Recommended Action:** * Offer clear and actionable recommendations for each defect: * Repair (if feasible and safe) * Replacement * Further inspection or testing * Prioritize safety in your recommendations. **Additional Considerations:** * **Image Quality:** Please ensure the image is of high resolution and adequately lit to facilitate accurate analysis. * **Contextual Information:** If available, provide additional context such as the part's age, usage history, or any recent events that might be relevant to the defects. """
            
            response = model.generate_content(
            [
            
                Part.from_uri(
                    file_url,
                    mime_type="image/jpeg",
                ),
                prompt
            ]
            
            
            )
            
            #detailed_analysis=response.candidates[0].content.parts[0].text
            detailed_analysis=response.text
            prompt=f"use detailed analysis of Automobile defect analyis {detailed_analysis} and provide two paragraph summary of just one major defect details" 

            response = model.generate_content(prompt)
            
            defect_detail=response.text
            
            response = model.generate_content(
            [defect_prompt.format(defect_detail=defect_detail)] 
            
        )
            defect_cateogy=response.text

            return detailed_analysis,defect_detail,defect_cateogy
        else: 
            
            prompt="""Analyze the attached video of an automobile part and indetify the defect, provide description to help categorize the defect"""

        
    
            
            response = model.generate_content(
            [
            
                Part.from_uri(
                    file_url,
                    mime_type="video/mp4",
                ),
                prompt
            ]
            
            
            )
        
            
            
            detailed_analysis=response.text
            prompt=f"use detailed analysis of Automobile defect analyis {detailed_analysis} and provide two paragraph summary of just one major defect details" 
            
            response = model.generate_content(prompt)
            
            defect_detail=response.text
        

            response = model.generate_content(
            [defect_prompt.format(defect_detail=defect_detail)] 
            )
            
            defect_cateogy=response.text
            return detailed_analysis,defect_detail,defect_cateogy
    except Exception as e: 
        print (e)
        


def upload_blob( source_file_name, destination_blob_name):
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    
    return blob.public_url
    

def file_exists(filepath):
  fname = filepath.split('/')[-1]
  val = bucket.get_blob(fname)
  if val is not None:
      return True
  else:
      return False


def video_analysis(videofile):
    file_name, file_extension=os.path.splitext(videofile)
    detailed_analysis=""
    defect_detail=""
    defect_cateogy=""
    detailed_analysis,defect_detail,defect_cateogy=analyse_defects(videofile,"Video")
    return detailed_analysis,defect_detail,defect_cateogy

def Image_analysis(imagefile):
    file_name, file_extension=os.path.splitext(imagefile.name)
    detailed_analysis=""
    defect_detail=""
    defect_cateogy=""
    if not file_exists(imagefile.name):
        with NamedTemporaryFile(dir='.', suffix=file_extension) as f:
            f.write(imagefile.getbuffer())
            public_url=upload_blob(f.name, imagefile.name)
            img_url="gs://gemvendordemo/" +imagefile.name

            detailed_analysis,defect_detail,defect_cateogy=analyse_defects(img_url,"Image")
            #create_recipe(ingredients,cuisine,diet)
    else:
        img_url="gs://gemvendordemo/" +imagefile.name
        #st.write(img_url)
        #st.image(img_url)
        detailed_analysis,defect_detail,defect_cateogy=analyse_defects(img_url,"Image")
        
    return detailed_analysis,defect_detail,defect_cateogy


def ResetSession():
    for key in st.session_state.keys():
        del st.session_state[key]