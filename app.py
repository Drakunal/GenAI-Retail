from dotenv import load_dotenv
load_dotenv() ## load all the environment variables

import numpy as np
import cv2
import streamlit as st
import os
import mysql.connector
from PIL import Image
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

## Function to load Gemini model and get responses
def get_gemini_response_from_image(input,image):
    model=genai.GenerativeModel('gemini-pro-vision')
    if input!="":
       response = model.generate_content([input,image])
    else:
       response = model.generate_content(image)
    print("\n Item identified: ",response.text)
    return response.text

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
    the SQL command will be something like this SELECT aisle_number 
        FROM products 
        WHERE brand = 'Pantene' 
        AND aisle_number = (
            SELECT aisle_number 
            FROM products 
            WHERE product_name LIKE '%shampoo%' 
            OR category LIKE '%shampoo%' 
            OR sub_category LIKE '%shampoo%'
        );
        \nExample 5 - Show me the brand, product name and amount_left_in_inventory and also aisle number where I can get the product with category or sub category or product name as Toothpaste
        the SQL command will be something like this 
            SELECT product_name,brand,amount_left_in_inventory,aisle_number 
            FROM products 
            WHERE product_name LIKE '%toothpaste%' 
            OR category LIKE '%toothpaste%' 
            OR sub_category LIKE '%toothpaste%'
        ); 
        if item is in plural form, you can use only the root word of that word to seach for it.
        Fot items which are a combination of more than 1 word, take the important word and do. Example 1- for lipstick, lipbalm, you can use lip. 
        Example 2- football, volleyball, and so on, just use ball. remember basket or foot is not important word here, ball is the important word.
        Example 3- For toothbrush, toothpaste and all similar words, use important word as tooth and the write the SQL query.
        Never identify humans or person or animals, only focus on the products portrayed in the image.
    """


]

## Streamlit App

st.set_page_config(page_title="SQL LLM")
st.header("Retail Store LLM")

image_question = "what is the thing in this image? Give one word answer only, never give more than 1 word answer. Make it a general answer. Do not give brand name. Do not answer human, person or animal, identify just the item in the image "
# question=st.text_input("Input: ",key="input")
question = "Show me the brand, product name and amount_left_in_inventory and also aisle number where I can get the product with category or sub category or product name as "
uploaded_file = st.file_uploader("Upload an image")
image=""  
md = """
| Product Name  | Brand | Inventory | Aisle number |
| :------------ | :--------------- | :---------------| :---------------|
| 
"""
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    image_np = np.array(image)  # Convert PIL Image to NumPy array
    face_detect = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml') 
    face_data = face_detect.detectMultiScale(image_np, 1.3, 5) 
    # Draw rectangle around the faces which is our region of interest (ROI) 
    for (x, y, w, h) in face_data: 
        cv2.rectangle(image_np, (x, y), (x + w, y + h), (255, 0, 0), 10) 
        roi = image_np[y:y+h, x:x+w] 
        # applying a gaussian blur over this new rectangle area 
        roi = cv2.medianBlur(roi, 101)

        # impose this blurred image on original image to get final image 
        image_np[y:y+roi.shape[0], x:x+roi.shape[1]] = roi 
    # Convert NumPy array back to PIL Image for display
    image = Image.fromarray(image_np)
    st.image(image, caption="Uploaded Image.", width=400)

submit=st.button("Find your products")

# if submit is clicked
if uploaded_file is not None and submit:
    response = get_gemini_response_from_image(image_question,image)
    question = question + response + "?"
    response = get_gemini_response(question,prompt)
    print(response)
    response = read_sql_query(response,mydb)
    st.subheader("Output")
    for row in response:
        print(row)
        md = md + " | "+str(row[0])+" | "+str(row[1])+" | "+str(row[2])+" | "+str(row[3])
        md = md + "\n"
    st.markdown(md
,
unsafe_allow_html=True,
)
        # for i in len(row):
        #     answer = answer + str(i)
        #     st.header(answer)
        # row.replace("(","")
        # row.replace(",","")
        