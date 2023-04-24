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
    # add try catch
    try:

        # Define app title and sidebar options
        st.set_page_config(page_title="DataChat App")
        st.sidebar.title("DataChat App")
        db_name = st.sidebar.text_input("Enter database name")
        db_collections = []
        if db_name:
            if st.sidebar.button("Connect"):
                db = client[db_name]
                db_collections = db.list_collection_names()
                for col in db_collections:
                    st.sidebar.write(col)

        if len(db_collections) > 0:
            if st.sidebar.button("Train model"):
                schema = ""
                for col in db_collections:
                    try:
                        print(col)
                        fields = db[col].find_one().keys()
                        schema += f"Collection: {col}\n"
                        for field in fields:
                            print(field)
                            schema += f"{col}.{field}\n"
                        st.write(
                            f"Collection: {col} - Fields: {', '.join(fields)}")
                    except:
                        st.write(f"No data found in collection: {col}")
                        continue

                print(schema)
                print("Fine-tuning model with schema...", schema)
                st.write("Fine-tuning model with schema...", schema)
                train_data = prepare_train_data(schema)
                fine_tuned_model = fine_tune_model(train_data)
                st.success("Fine-tuned GPT-3 model with schema successfully!")
                st.write("Fine-tuning model with WikiSQL data...")
                train_data = prepare_train_data(
                    schema + "\n" + fine_tuned_model.choices[0].text.strip())
                fine_tuned_model = fine_tune_model(train_data)
                st.success(
                    "Fine-tuned GPT-3 model with WikiSQL data successfully!")

                if st.sidebar.button("Generate SQL query"):
                    st.write("Ask a question and get a SQL query as a response:")
                    question = st.text_input("Question")
                    if question:
                        results = generate_query(question)
                        st.write(results)
                    else:
                        st.warning("Enter a question to generate a SQL query")
            else:
                st.warning("Select at least one collection to use the app")
        else:
            st.warning("Enter database name to connect")

        # Define app content
        st.title("DataChat App")
        if db is not None:
            st.write(f"Connected to database '{db_name}'")
            if len(db_collections) > 0:
                st.write(f"Selected collections: {', '.join(db_collections)}")

    except Exception as e:
        st.write(e)


# Run app
if __name__ == "__main__":
    app()
