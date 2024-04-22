import os
import openai
import streamlit as st
from openai import OpenAI

# Set up your OpenAI API key
client = OpenAI(api_key="OPEN API KEY")

# Create a wrapper function to get OpenAI completion
def get_completion(prompt, model="gpt-3.5-turbo"):
    completion = client.chat.completions.create(
        model=model,
        messages=[
        {"role": "system", "content": 'You are a helpful chatbot. Answer any questions about the effects of exposure to high noise levels and noise in general. If asked a question not related to noise or sound, apologize and ask for another question.'},
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
        # Create a placeholder for the info message
        info_placeholder = st.empty()

        # Display the "Fetching information..." message in the placeholder
        info_placeholder.info("Fetching information...")

        # Get the completion and overwrite the info message with the result
        completion = get_completion(prompt)
        
        # Overwrite the info message with a success message
        info_placeholder.success("Information fetched successfully!")

        # Display the completion
        st.write(completion)

# # Display educational information on noise exposure
# st.header("Educational Information")
# st.subheader("Short-term Effects of Noise Exposure")
# st.write("""
# - Temporary hearing loss or tinnitus
# - Increased stress levels
# - Sleep disturbances
# """)

# st.subheader("Long-term Effects of Noise Exposure")
# st.write("""
# - Permanent hearing loss
# - Cardiovascular issues
# - Cognitive impairment
# """)

# st.subheader("Solutions to Noise Issues")
# st.write("""
# - Use of earplugs or noise-canceling headphones
# - Implementing noise reduction strategies in the workplace
# - Regular hearing check-ups
# """)

# Add a sidebar with additional resources
st.sidebar.header("Additional Resources")
st.sidebar.write("Here are some helpful links for further reading:")
st.sidebar.write("[Occupational Noise Exposure - Health Effects](https://www.osha.gov/noise/health-effects)")
st.sidebar.write("[Understand Noise Exposure | NIOSH | CDC](https://www.cdc.gov/niosh/topics/noise/preventoccunoise/understand.html)")
st.sidebar.write("[Health Effects of Noise Pollution - Medical News Today](https://www.medicalnewstoday.com/articles/noise-pollution-health-effects)")
st.sidebar.write("[Noise - World Health Organization (WHO)](https://www.who.int/europe/news-room/fact-sheets/item/noise)")

# Ensure to set the OPENAI_API_KEY environment variable before running the app
