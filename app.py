import streamlit as st
import requests
import pandas as pd
from utils.chart_generator import generate_chart

# Configure Streamlit page layout and theme
st.set_page_config(
    page_title="Apex Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_URL = "http://localhost:5001"

# Main Title and Description
st.title("📈 Apex Analytics")
st.markdown("### Conversational AI for Instant Business Intelligence Dashboards")
st.markdown("---")

# Sidebar for controls and file upload
with st.sidebar:
    st.header("1. Upload Data")
    st.markdown("Upload a CSV file to begin querying.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    
    if st.button("Load Dataset", type="primary"):
        if uploaded_file is not None:
            with st.spinner("Uploading and processing dataset..."):
                try:
                    # Send file to Flask backend
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'text/csv')}
                    response = requests.post(f"{API_URL}/upload", files=files)
                    
                    if response.status_code == 200:
                        st.session_state['data_loaded'] = True
                        st.session_state['schema'] = response.json().get('schema')
                        st.success(f"Successfully loaded {uploaded_file.name}!")
                    else:
                        st.error(f"Failed to load dataset: {response.json().get('error', 'Unknown Error')}")
                except requests.exceptions.ConnectionError:
                    st.error("Error connecting to the backend server. Is Flask running?")
        else:
            st.warning("Please upload a file first.")
            
    # Show Schema if loaded
    if st.session_state.get('data_loaded'):
        with st.expander("View Dataset Schema"):
            st.code(st.session_state.get('schema', 'Schema not available'), language="text")

# Main content area - Query and Results
st.header("2. Ask Questions")
user_query = st.text_input(
    "Ask a question in plain English:",
    placeholder="e.g., Show the total revenue by region"
)

# Only process if user sends query
if st.button("Generate Dashboard"):
    if not st.session_state.get('data_loaded'):
        st.warning("Please upload and load a dataset from the sidebar first.")
    elif not user_query:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Analyzing data and generating dashboard..."):
            try:
                 # Send query request to backend
                 payload = {"prompt": user_query}
                 response = requests.post(f"{API_URL}/query", json=payload)
                 
                 if response.status_code == 200:
                      result = response.json()
                      data = result.get('data', [])
                      chart_config = result.get('chart_config', {})
                      query_details = result.get('query_details', {})
                      
                      if len(data) == 0:
                          st.info("The query executed successfully but returned no data.")
                      else:
                          # Container for layout
                          col1, col2 = st.columns([2, 1])
                          
                          with col1:
                               st.subheader("Visualization")
                               # Generate chart locally using the data returned by backend
                               fig = generate_chart(data, chart_config)
                               if fig:
                                   st.plotly_chart(fig, use_container_width=True)
                               else:
                                   st.warning("Could not generate a chart for this data. Showing table only.")
                                   
                          with col2:
                               st.subheader("Data View")
                               # Display data natively as user requested
                               df_view = pd.DataFrame(data)
                               st.dataframe(df_view, use_container_width=True)
                               
                          # Show details in an expander
                          with st.expander("Query Details & SQL Statement"):
                               st.markdown("**Explanation:**")
                               st.write(query_details.get('explanation', "No explanation provided."))
                               st.markdown("**Generated SQL:**")
                               st.code(query_details.get('generated_sql', ""), language="sql")
                               
                 else:
                     error_data = response.json()
                     st.error(f"Error: {error_data.get('error', 'Unknown error occurred')}")
                     if 'generated_sql' in error_data:
                         with st.expander("View Failed SQL"):
                             st.code(error_data['generated_sql'], language="sql")
                             st.error(error_data.get('sql_error', ''))
            except requests.exceptions.ConnectionError:
                 st.error("Error connecting to the backend server. Is Flask running?")
