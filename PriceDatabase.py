import streamlit as st
import pandas as pd
import random
import requests
from io import BytesIO

# GitHub repository configuration
GITHUB_RAW_BASE_URL = "https://raw.githubusercontent.com/Gremcool/gremcool/main"
EXCEL_FILES_PATH = "excel_files"
LOGO_PATH = "assets/logo.png"  # Adjust this to your logo's path in the repository

# List of filenames to load from the GitHub repository
EXCEL_FILE_NAMES = [
    "FINAL MASTER LIST AS OF 24 JULY 2024.xlsx",
    "First Draft PriceList.xlsx",
    "SA Price List.xlsx",  # Add all your file names here
]

# Custom CSS for page layout and styling
st.markdown(
    """
    <style>
    /* Remove extra margins around the main container */
    .main .block-container {
        padding: 0;
        margin: 0;
        max-width: 90%;
    }
    /* Center and style the header banner */
    .header-banner {
        background-color: #004080;
        color: white;
        text-align: center;
        padding: 20px 0;
        border-radius: 5px;
        font-size: 24px;
        font-weight: bold;
    }
    /* Adjust table styling */
    .dataframe {
        width: 100% !important;
        text-align: left;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Function to fetch files from GitHub
def load_files_from_github():
    files = {}
    for file_name in EXCEL_FILE_NAMES:
        file_url = f"{GITHUB_RAW_BASE_URL}/{EXCEL_FILES_PATH}/{file_name}"
        response = requests.get(file_url)
        if response.status_code == 200:
            file_data = pd.read_excel(BytesIO(response.content))
            files[file_name.split(".")[0]] = file_data
        else:
            st.warning(f"Failed to load {file_name} from GitHub. Please check the URL.")
    return files

# Function to fetch logo from GitHub
def load_logo_from_github():
    logo_url = f"{GITHUB_RAW_BASE_URL}/{LOGO_PATH}"
    response = requests.get(logo_url)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        st.warning("Failed to load the logo from GitHub.")
        return None

# Function to style DataFrame and highlight matches
def highlight_matches(data, query):
    return data.style.applymap(
        lambda val: "background-color: yellow" if query.lower() in str(val).lower() else ""
    ).set_table_styles(
        [
            {
                "selector": "thead th",
                "props": [
                    ("background-color", "black"),
                    ("color", "white"),
                    ("text-align", "center"),
                ],
            }
        ]
    )

# Function to search across files and highlight results
def search_across_files(query, files):
    result = {}
    for file_name, data in files.items():
        matches = data[data.apply(lambda row: row.astype(str).str.contains(query, case=False, na=False).any(), axis=1)]
        if not matches.empty:
            result[file_name] = highlight_matches(matches, query)
    return result

# Main function for the app
def main():
    # Load the logo
    logo = load_logo_from_github()

    # Display header banner with RMS logo
    st.markdown('<div class="header-banner">RMS Data Explorer</div>', unsafe_allow_html=True)
    if logo:
        st.image(logo, width=150, use_column_width=False)

    # Load files from GitHub
    st.write("Loading files from GitHub...")
    uploaded_files = load_files_from_github()

    # Predictive search bar
    search_query = st.text_input("Enter your search query:")
    if st.button("Clear Search"):
        search_query = ""

    # Display search results or all files
    if search_query:
        st.header("Search Results")
        search_results = search_across_files(search_query, uploaded_files)
        if search_results:
            for file_name, styled_data in search_results.items():
                title_bg_color = "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                st.markdown(f"<div style='background-color: {title_bg_color}; padding: 10px; border-radius: 5px; color: white;'>{file_name}</div>", unsafe_allow_html=True)
                st.write(styled_data)
        else:
            st.write("No matches found.")
    else:
        st.header("All Files")
        for file_name, data in uploaded_files.items():
            title_bg_color = "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            st.markdown(f"<div style='background-color: {title_bg_color}; padding: 10px; border-radius: 5px; color: white;'>{file_name}</div>", unsafe_allow_html=True)
            st.write(data.head())  # Show preview of the data

if __name__ == "__main__":
    main()
