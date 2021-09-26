import requests
import json
import streamlit as st
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import csv
from fast_autocomplete.misc import read_csv_gen
from fast_autocomplete import AutoComplete
from io import StringIO
def call_api(search_query):
    url = "https://inference.hackzurich2021.hack-with-admin.ch/api/question/hack_zurich"

    payload = json.dumps({
    "question": search_query
    })
    headers = {
    'X-API-KEY': 'sjNmaCtviYzXWlS',
    'Content-Type': 'application/json'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)

    try:
        response_res = response.json()
        col1,col2 = st.columns([1,2])

        st.success("Done!")
        col1.markdown("### Result")
        col1.code(str(response_res['result']))
        col2.markdown("### SQL")
        col2.code(response_res['sql'])
    except:
        st.warning("Connection error, please re-enter query")
st.title("Valuexplorer")
container = st.container()

st.write("This tool allows you to navigate \ncomplex databases via simple queries!")
functionality = st.selectbox("Functionality", ["Search database using ValueNet", "Deepdive into raw-data", "Feedback"])

if functionality == "Search database using ValueNet":

    st.subheader("Categories")

    opt = st.multiselect("View results categorized according to your preference", ["Automobile","Education","Finance","Public Policy", "Science"], default="Automobile", key=None, help="Please enter your preferences here, leave blank if you have none", on_change=None, args=None, kwargs=None)



    search_query = st.text_input("Search...", value='How many cars were sold in total in the year of 2020?', max_chars=None, key=None, type='default', help="Please enter your search query here", autocomplete="enter", on_change=None, args=None, kwargs=None)
    if st.button("Submit"):
        # with st.expander("See example"):
        #   st.write("here's the example",expanded=False)
        # ==========================API call====================
        call_api(search_query)

    text = '''
    ---
    '''

    st.markdown(text)
    st.subheader("Need help with queries?")
    st.write(f"Don't worry! we can autogenerate possible questions with simple keywords! \n Enter a keyword pertaining to any topic and see the possible questions.")
    #Format Search query into request and return response
    def get_words(path):
        colnames = ['questions', 'queries', 'answers']
        data = pd.read_csv(path, names=colnames)
        return data.questions.tolist()
    words = get_words("questions_queries_python.csv")
    words[0] = ''
    col1,col2 = st.columns([10,3])
    keyword = col1.selectbox("list of queries indexed by keywords/synonyms", words)
    st.text("Full query:")
    st.code(keyword, language="python")
    # if(keyword!=''):
    #     call_api(keyword)



elif functionality == "Deepdive into raw-data":


    st.title('Deepdive into source data:')
    st.session_state['raw_data'] = False
    def load_data(dataset,nrows):
        if dataset=='Indication_Values':
            DATA_URL = ('./EN_indicator_data.csv')
            data = pd.read_csv(DATA_URL, nrows=nrows)
            return data
        if dataset=='ENT_data':
            DATA_URL = ('./ENT_data.csv')
            data = pd.read_csv(DATA_URL, nrows=nrows)
            # st.write(data)
            return data

    # DATE_COLUMN = 'date/time'
    option = st.selectbox('Select Dataset: ',['Indication_Values','ENT_data'])
        
    data = load_data(option,100)
    

    cols_data = data.columns.to_list()
    pick_cols = st.multiselect('Select columns:', cols_data)
    colk, colj = st.columns([0.3,1])

    if colk.button('Show raw data'):
        st.session_state['raw_data'] = True
    if colj.button("Hide raw data"):
        st.session_state['raw_data'] = False

    if st.session_state['raw_data']:
        st.subheader('Raw data')
        
        if pick_cols!=[] and pick_cols!=None:
            st.write(data[pick_cols])

        # st.write(data)
        

    st.subheader('Visualizing source data')
    st.write("Understanding relationship between different variables in the data:" )

    viz_type = st.selectbox('Select visualization type:',['Line Chart','Area Chart','Bar Chart','Map','Pie Chart','table'],help='Select visualization type from given options')
    columnns_temp = []
    data_2 = []
    if viz_type == 'Line Chart':

        X = st.selectbox('X_axis', cols_data,help='Select variable for X-axis that is required to represent the relationship')
        Y = st.multiselect('Y_axis', cols_data,help='Select variable(s) for Y-axis that is required to represent the relationship')
        # x_vals_1 = [ i for i in range(3,21)]
        # st.write(X,Y)
        if Y==[] or Y==None:
            st.warning('Please select atleast one variable for Y-axis')
        else:
            temp_values = [i for i in Y]
            temp_values = temp_values.append(X)
            columnns_temp = Y
            columnns_temp.append(X)
            # st.write(columnns_temp)

            data_2 = data[columnns_temp]
            # st.write(data_2)
            # st.write(columnns_temp)
            # cols = cols.extend(Y)
            
            # data_2 = data[cols]
            # st.write(data_2)
            # # Create a list of data to be  represented in y-axis
            try:
                chart_data = data_2.reset_index(drop=True).melt(X)
                data = alt.Chart(chart_data).mark_line().encode(x=X,y='value',color='variable')
                st.altair_chart(data,use_container_width=True)
            except:
                st.warning('Please select appropriately typed values for X and Y')

    elif viz_type == 'Area Chart':
        columnns_temp = []
        X = st.selectbox('X_axis', cols_data,help='Select variable for X-axis that is required to represent the relationship')
        Y = st.multiselect('Y_axis', cols_data,help='Select variable(s) for Y-axis that is required to represent the relationship')
        # x_vals_1 = [ i for i in range(3,21)]
        # st.write(X,Y)
        temp_values = [i for i in Y]
        temp_values = temp_values.append(X)
        columnns_temp = Y
        columnns_temp.append(X)
        # st.write(columnns_temp)

        data_2 = data[columnns_temp]
        
        try:
            chart_data = data_2.reset_index(drop=True).melt(X)
            data = alt.Chart(chart_data).mark_area().encode(x=X,y='value',color='variable')
            st.altair_chart(data,use_container_width=True)
        except :
            st.warning('Please select appropriately typed values for X and Y')

    elif viz_type == 'Bar Chart':
        columnns_temp = []
        X = st.selectbox('X_axis', cols_data,help='Select variable for X-axis that is required to represent the relationship')
        Y = st.selectbox('Y_axis', cols_data,help='Select variable for Y-axis that is required to represent the relationship')
        # x_vals_1 = [ i for i in range(3,21)]
        # st.write(X,Y)
        columnns_temp = [Y]
        columnns_temp.append(X)
        # st.write(columnns_temp)
        data_2 = data[columnns_temp]

        try:
            chart_data = data_2.reset_index(drop=True).melt(X)
            data = alt.Chart(chart_data).mark_bar().encode(x=X,y='value',color='variable')
            st.altair_chart(data,use_container_width=True)
        except :
            st.warning('Please select appropriately typed values for X and Y')

    elif viz_type == 'table':
        X = st.selectbox('X_axis', cols_data,help='Select variable for X-axis that is required to represent the relationship')
        Y = st.multiselect('Y_axis', cols_data,help='Select variable(s) for Y-axis that is required to represent the relationship')
        # x_vals_1 = [ i for i in range(3,21)]
        st.write(X,Y)
        temp_values = [i for i in Y]
        temp_values = temp_values.append(X)
        columnns_temp = Y
        columnns_temp.append(X)
        st.write(columnns_temp)

        data_2 = data[columnns_temp]
        st.write(data_2)


elif functionality == "Feedback":

    st.text_area("Please leave your feedback and suggestions here:")
    if st.button("Submit"):
        st.success("Thanks for your feedback!")


hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 