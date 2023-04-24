import openai
import pymongo
import vaex
import pandas as pd
import streamlit as st
import requests

# Authenticate to OpenAI API
openai.api_key = "YOUR_API_KEY"

# Define MongoDB client
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = None

# Load WikiSQL data with Vaex
train = vaex.open('wikisql/train.csv')
valid = vaex.open('wikisql/validation.csv')
test = vaex.open('wikisql/test.csv')

# Convert Vaex DataFrame to Pandas DataFrame
train = train.to_pandas_df()
valid = valid.to_pandas_df()
test = test.to_pandas_df()

# Concatenate train and valid dataframes
data = pd.concat([train, valid], ignore_index=True)

# Define function to prepare training data for OpenAI GPT-3


def prepare_train_data(schema):
    train_data = schema
    for i in range(len(data)):
        question = data.iloc[i]['question']
        sql = data.iloc[i]['sql']
        train_data += question + "\n" + sql + "\n"
    return train_data

# Define function to fine-tune GPT-3 on WikiSQL data


def fine_tune_model(train_data):
    fine_tuned_model = openai.Completion.create(
        engine="davinci",
        prompt=train_data,
        temperature=0.5,
        max_tokens=2048,
        n_epochs=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return fine_tuned_model

# Define function to call Flask API


def generate_query(question):
    url = "http://localhost:5000/query"
    payload = {"question": question}
    response = requests.post(url, json=payload)
    return response.json()['data']

# Define Streamlit app


def app():
    global db

    # Define app title and sidebar options
    st.set_page_config(page_title="OpenAI WikiSQL App")
    st.sidebar.title("OpenAI WikiSQL App")
    db_name = st.sidebar.text_input("Enter database name")
    db_collections = []
    if db_name:
        db = client[db_name]
        collections = db.list_collection_names()
        if len(collections) > 0:
            db_collections = st.sidebar.multiselect(
                "Select collections", collections)
    if len(db_collections) > 0:
        fine_tune = st.sidebar.checkbox(
            "Fine-tune GPT-3 with selected collections?")
        if fine_tune:
            schema = ""
            for col in db_collections:
                fields = db[col].find_one().keys()
                schema += f"Collection: {col}\n"
                for field in fields:
                    schema += f"{col}.{field}\n"
            train_data = prepare_train_data(schema)
            fine_tuned_model = fine_tune_model(train_data)
            st.success("Fine-tuned GPT-3 model successfully!")

    # Define app content
    st.title("OpenAI WikiSQL App")
    if db:
        st.write(f"Connected to database '{db_name}'")
        if len(db_collections) > 0:
            st.write(f"Selected collections: {', '.join(db_collections)}")
            if fine_tune:
                st.write("GPT-3 model fine-tuned with selected collections!")
                st.write("Ask a question and get a SQL query as a response:")
                question = st.text_input("Question")
                if question:
                    results = generate_query(question)
                    st.write(results)
        else:
            st.warning("Select at least one collection touse the app")
    else:
        st.warning("Enter database name to connect")


# Run Streamlit app
if __name__ == "__main__":
    app()
