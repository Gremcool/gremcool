import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials
import io
import random

# Authenticate and initialize Google Drive API
def get_drive_service():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_service_account_file("path_to_your_service_account.json", scopes=SCOPES)
    return build("drive", "v3", credentials=credentials)

# Fetch Excel files from a specific Google Drive folder
def fetch_excel_files_from_drive(folder_id):
    service = get_drive_service()
    results = service.files().list(
        q=f"'{folder_id}' in parents and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'",
        fields="files(id, name)"
    ).execute()
    files = results.get("files", [])
    excel_files = {}
    
    for file in files:
        request = service.files().get_media(fileId=file["id"])
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        file_stream.seek(0)
        excel_files[file["name"]] = pd.read_excel(file_stream)
    
    return excel_files

# Function to style DataFrame and highlight matches
def highlight_matches(data, query):
    """Highlight cells containing the search query in yellow."""
    return data.style.applymap(
        lambda val: "background-color: yellow" if query.lower() in str(val).lower() else ""
    ).set_table_styles(
        [
            {
                "selector": "thead th",
                "props": [
                    ("background-color", "black"),
                    ("color", "white"),
                    ("font-weight", "bold"),
                    ("text-align", "center"),
                ],
            }
        ]
    )

# Function to search across files and highlight results
def search_across_files(query, files):
    """Search for the query in all uploaded files and return highlighted results."""
    result = {}
    for file_name, data in files.items():
        matches = data[data.apply(lambda row: row.astype(str).str.contains(query, case=False, na=False).any(), axis=1)]
        if not matches.empty:
            result[file_name] = highlight_matches(matches, query)
    return result

# Main function to display the app
def main():
    st.title("Search Price Lists")

    # Load files into session state if not already loaded
    if "uploaded_files" not in st.session_state:
        folder_id = "your_google_drive_folder_id"  # Replace with your folder ID
        st.session_state.uploaded_files = fetch_excel_files_from_drive(folder_id)

    # Predictive search bar
    search_query = st.text_input("Enter your search query:", key="search")
    st.session_state.search_query = search_query

    # Clear search button
    if st.button("Clear Search"):
        st.session_state.search_query = ""

    # Display search results or uploaded files
    if st.session_state.search_query:
        st.markdown("### Search Results")
        search_results = search_across_files(st.session_state.search_query, st.session_state.uploaded_files)
        if search_results:
            for file_name, styled_data in search_results.items():
                title_bg_color = "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                st.markdown(f"<div style='background-color: {title_bg_color}; padding: 10px; color: white;'>{file_name}</div>", unsafe_allow_html=True)
                st.write(styled_data)
        else:
            st.write("No matches found across the uploaded files.")
    else:
        if st.session_state.uploaded_files:
            for file_name, data in st.session_state.uploaded_files.items():
                title_bg_color = "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                st.markdown(f"<div style='background-color: {title_bg_color}; padding: 10px; color: white;'>{file_name}</div>", unsafe_allow_html=True)
                st.write(data.head())  # Show preview of the uploaded files

# Run the app
if __name__ == "__main__":
    main()
