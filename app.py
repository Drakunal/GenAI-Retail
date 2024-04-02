from dotenv import load_dotenv
load_dotenv() ## load all the environment variables

import streamlit as st
import os
import mysql.connector

import google.generativeai as genai

## Configure GenAI Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

#DB Connection and configuration
mydb = mysql.connector.connect(
    host = os.getenv("host"),
    user = os.getenv("user"),
    password = os.getenv("password"),
    database = "retail_store2"
)

## Function To Load Google Gemini Model and provide queries as response
def get_gemini_response(question,prompt):
    model=genai.GenerativeModel('gemini-pro')
    response=model.generate_content([prompt[0],question])
    return response.text

## Function To retrieve query from the database

def read_sql_query(sql,db):
    cur=db.cursor()
    cur.execute(sql)
    rows=cur.fetchall()
    for row in rows:
        print(row)
    return rows

## Define Your Prompt
prompt=[
    """
    You are an expert in converting English questions to SQL query!
    The SQL database has the table named products and has the following columns - 
product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    brand VARCHAR(100),
    category VARCHAR(100),
    sub_category VARCHAR(100),
    price_per_unit DECIMAL(10, 2) NOT NULL,
    amount_left_in_inventory INT NOT NULL,
    aisle_number INT,
    weight DECIMAL(10, 2),
    country_of_origin VARCHAR(100),
    manufacturer VARCHAR(100),
    supplier VARCHAR(100).
\n\nFor example,\nExample 1 - How many entries of records are present?, 
    the SQL command will be something like this SELECT COUNT(*) FROM products ;
    \nExample 2 - Tell me all the products which are from the brand Nike, 
    the SQL command will be something like this SELECT * FROM products
    where brand="Nike"; 
    \nExample 3 - List all the price and products names of all Nike Products which are shirt, 
    the SQL command will be something like this SELECT price, product_name FROM products
    WHERE brand = 'Nike' AND category = 'shirt';
    also the sql code should not have ``` in beginning or end and sql word in output
    \nExample 4 - In which aisle is pantene shampoo present, 
    the SQL command will be something like this Select aisle_number from products where
    brand = "Pantene" AND product_name = "shampoo"
    """


]

## Streamlit App

st.set_page_config(page_title="SQL LLM")
st.header("Retail Store LLM")

question=st.text_input("Input: ",key="input")

submit=st.button("Ask the question")

# if submit is clicked
if submit:
    response=get_gemini_response(question,prompt)
    print(response)
    response=read_sql_query(response,mydb)
    st.subheader("Output")
    for row in response:
        print(row)
        st.header(row)