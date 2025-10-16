import streamlit as st
from processing import process
from qdrant_utils import create_collection
from query import fetch_query

create_collection()

uploaded_file = st.file_uploader("Upload a file", type=["png", "jpg", "txt", "pdf", "mp3"])

if uploaded_file is not None:
    st.write(f"File uploaded: `{uploaded_file.name}`")

    with st.spinner("Processing... Please wait."):
        try:
            result = process(uploaded_file)
            message = result[1] if len(result) > 1 else None
            st.write(message or "Processing complete.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
        finally:
            uploaded_file = None

query = st.text_input("Enter your query")

if st.button("Run Query") and query:
    with st.spinner("Running your query..."):
        try:
            response = fetch_query(query)
            st.markdown("### Response")
            st.write(response)
        except Exception as e:
            st.error(f"An error occurred: {e}")
