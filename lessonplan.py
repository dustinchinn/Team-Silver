import os
import openai
import streamlit as st
from openai import OpenAI

client = OpenAI(api_key='your-api-key') 

# create a wrapper function
def get_completion(prompt, model="gpt-3.5-turbo"):
    completion = client.chat.completions.create(
        model=model,
        messages=[
        {"role": "system", "content": 'You are a helpful assistant. Write a lesson on the effects of exposure to high noise levels. The lesson should cover short-term and long-term effects as well as ways to mitigate loud noise and its effects. Come up with some examples that show common effects of noise exposure and solutions to remedy the effects.'},
        {"role": "user", "content": prompt},
        ]
    )
    return completion.choices[0].message.content

# create our streamlit app
with st.form(key = "chat"):
    prompt = st.text_input("Enter a question about high noise levels you would like me to explain: ") # TODO!
    
    submitted = st.form_submit_button("Submit")
    
    if submitted:
        st.write(get_completion(prompt))

