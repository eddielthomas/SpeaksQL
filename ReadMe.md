DataChat App

DataChat is a web application that uses OpenAI's GPT-3 to generate SQL queries from natural language questions. It connects to a MongoDB database to extract the schema information and use it to fine-tune the GPT-3 model on the user's data. The application is built with Python, Streamlit, and Flask.

Not this app needs further testing but serves as a POC....

Features

Connect to a MongoDB database
View the schema information for selected collections
Fine-tune the GPT-3 model on the schema information and WikiSQL data
Generate SQL queries from natural language questions using the fine-tuned model

Installation

Clone the repository to your local machine
Create a virtual environment and activate it
Install the dependencies using pip install -r requirements.txt
Set your OpenAI API key as an environment variable named OPENAI_API_KEY
Start the Flask API by running python api.py
Start the Streamlit app by running streamlit run app.py

Usage


Enter the name of your MongoDB database in the text input box in the sidebar.
Click the "Connect" button to connect to the database.
Select one or more collections from the list of collections in the sidebar.
Click the "Train model" button to fine-tune the GPT-3 language model on your database schema and the WikiSQL dataset.
Ask a natural language question in the text input box in the main area of the app.
Click the "Generate SQL query" button to generate a SQL query from your question.

Credits
The DataChat App was created by Eddie Thomas.

License
The DataChat App is released under the MIT License. See LICENSE for details.