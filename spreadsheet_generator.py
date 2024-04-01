import streamlit as st 
import os
from openai import OpenAI

client = OpenAI(api_key=('Your key API here'))

def create_spreadsheet(noise_data):
    # Construct the prompt for the OpenAI API
    prompt_text = "Create a CSV format with the columns: dB Level, Timestamp, Location, Comments. Here is the data:\n\n"
    for entry in noise_data:
        # Properly format the prompt to handle potential commas in the comments
        comments = entry['comments'].replace(',', ';')
        prompt_text += f"{entry['db_level']}, {entry['timestamp']}, {entry['location']}, \"{comments}\"\n"
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt_text}
        ],
        temperature=0.5,
        max_tokens=200,
        top_p=1
    )
    # Extract the formatted spreadsheet content from the response
    spreadsheet_content = response.choices[0].message.content
    return spreadsheet_content

def main():
    st.title('Noise Data Spreadsheet Creator')
    
    with st.form("noise_data_form"):
        db_level = st.number_input('dB Level', min_value=0, step=1)
        timestamp = st.text_input('Timestamp (YYYY-MM-DD HH:MM:SS)')
        location = st.text_input('Location')
        comments = st.text_area('Comments')
        submit_button = st.form_submit_button("Add to Spreadsheet")
        
        if 'noise_data' not in st.session_state:
            st.session_state.noise_data = []
        
        if submit_button:
            st.session_state.noise_data.append({
                "db_level": db_level, 
                "timestamp": timestamp, 
                "location": location, 
                "comments": comments
            })
            # Clear the form so the user can enter new data
            st.experimental_rerun()
    
    # Show the current data entries
    if st.session_state.noise_data:
        st.write("Current Data Entries:")
        for entry in st.session_state.noise_data:
            st.write(entry)

    if st.button('Create Spreadsheet'):
        if st.session_state.noise_data:
            # Call the create_spreadsheet function with the current data entries
            spreadsheet_content = create_spreadsheet(st.session_state.noise_data)
            st.text_area("Spreadsheet:", spreadsheet_content, height=300)
            st.download_button(
                label="Download Spreadsheet as CSV",
                data=spreadsheet_content,
                file_name='noise_data.csv',
                mime='text/csv',
        )
    else:
        st.warning("Please add some data before creating the spreadsheet.")

if __name__ == "__main__":
    main()
