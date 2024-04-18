import os
import openai
import streamlit as st
from openai import OpenAI

# Set up your OpenAI API key
client = OpenAI(api_key="INSERT-API-KEY-HERE")

# Create a wrapper function to get OpenAI completion
def get_completion(prompt, model="gpt-3.5-turbo"):
    completion = client.chat.completions.create(
        model=model,
        messages=[
        {"role": "system", "content": 'You are a helpful assistant. Write a lesson on the effects of exposure to high noise levels. The lesson should cover short-term and long-term effects as well as ways to mitigate loud noise and its effects. Come up with some examples that show common effects of noise exposure and solutions to remedy the effects.'},
        {"role": "user", "content": prompt},
        ]
    )
    return completion.choices[0].message.content

# Streamlit app
st.title("Noise Exposure Educational Tool")
st.write("Learn about the short-term and long-term effects of noise exposure and discover solutions to mitigate its impact.")

# Form for user input
with st.form(key="noise_query"):
    prompt = st.text_area("Enter your question or topic about noise exposure:", height=150)
    submitted = st.form_submit_button("Submit")

    if submitted and prompt:
        st.write("Fetching information...")
        st.write(get_completion(prompt))

# Display educational information on noise exposure
st.header("Educational Information")
st.subheader("Short-term Effects of Noise Exposure")
st.write("""
- Temporary hearing loss or tinnitus
- Increased stress levels
- Sleep disturbances
""")

st.subheader("Long-term Effects of Noise Exposure")
st.write("""
- Permanent hearing loss
- Cardiovascular issues
- Cognitive impairment
""")

st.subheader("Solutions to Noise Issues")
st.write("""
- Use of earplugs or noise-canceling headphones
- Implementing noise reduction strategies in the workplace
- Regular hearing check-ups
""")

# Add a sidebar with additional resources
st.sidebar.header("Additional Resources")
st.sidebar.write("Here are some helpful links for further reading:")
st.sidebar.write("[Occupational Noise Exposure - Health Effects](https://www.osha.gov/noise/health-effects)")
st.sidebar.write("[Understand Noise Exposure | NIOSH | CDC](https://www.cdc.gov/niosh/topics/noise/preventoccunoise/understand.html)")
st.sidebar.write("[Health Effects of Noise Pollution - Medical News Today](https://www.medicalnewstoday.com/articles/noise-pollution-health-effects)")
st.sidebar.write("[Noise - World Health Organization (WHO)](https://www.who.int/europe/news-room/fact-sheets/item/noise)")

# Ensure to set the OPENAI_API_KEY environment variable before running the app
