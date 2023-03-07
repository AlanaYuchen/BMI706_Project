import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to TCGA Explorer! 👋")

st.sidebar.success("Select a demo above.")

st.markdown(
    """
   The Cancer Genome Atlas (TCGA) is a publicly cancer database curated by the National Cancer Institute 
   and contains molecular data (including genomic, epigenomic, transcriptomic, and proteomic data) 
   of more than 20,000 primary cancer samples from patients and corresponding normal tissue samples 
   of 33 types of cancer. While the extensive scale of TCGA entails its popularity for cancer 
   studies, it can also be difficult to navigate this forest of data. 
   Feeling lost in the large database?  
   Here we come, the Illuminator Team!
   We offer an application that overviews clinical and family history data spanning all sequenced samples in TCGA!   
   We hope to help empower cancer researchers in interacting with the database more effectively 
   as they (1) survey types of research questions that may be answered using the available data i
   n TCGA or (2) evaluate whether TCGA would be a suitable data source for predefined research questions 
   they have in mind.   
   The data we used is publicly available at GDC data portal (https://portal.gdc.cancer.gov/repository).
   - 
"""
)