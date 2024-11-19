import streamlit as st

# original_title = '<h1 style="font-family: serif; color:white; font-size: 20px;">Suppler Forensics ✨ </h1>'

# st.markdown(original_title, unsafe_allow_html=True)

col1, col2 = st.columns([8, 1])
with col1:
    st.title("Supplier Forensics Agent using Gemini")
with col2:
    st.image("images/AAM_Logo.jpeg")

##todo: Change background URL
# Set the background image
background_image = """
<style>
[data-testid="stAppViewContainer"] > .main {
 /*   background-image: url("IMAGE URL"); */
    background-size: 100vw 80vh;  # This sets the size to cover 100% of the viewport width and height
    background-position: center;  
    background-repeat: no-repeat;
}
</style>
"""

st.markdown(background_image, unsafe_allow_html=True)

##st.text_input("", placeholder="Streamlit CSS ")

input_style = """
<style>
input[type="text"] {
    background-color: transparent;
    color: #a19eae;  // This changes the text color inside the input box
}
div[data-baseweb="base-input"] {
    background-color: transparent !important;
}
[data-testid="stAppViewContainer"] {
    background-color: transparent !important;
}
</style>
"""
st.markdown(input_style, unsafe_allow_html=True)