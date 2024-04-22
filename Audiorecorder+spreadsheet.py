import pyaudio
import wave
import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.express as px
import openai
import io

# Initialize OpenAI client
openai.api_key = "YOUR_OPENAI_API_KEY_HERE"  # Replace with your OpenAI API key

def record_audio(output_file, duration=5, sample_rate=44100, channels=1, format=pyaudio.paInt16):
    p = pyaudio.PyAudio()
    stream = p.open(format=format,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=1024)

    print("Recording...")

    frames = []
    for _ in range(0, int(sample_rate / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)

    print("Finished recording.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))

def main():
    st.title('Noise Data Spreadsheet Creator')
    # Initialize noise_data if it's not already initialized
    if "noise_data" not in st.session_state:
        st.session_state.noise_data = []
        
    with st.form("noise_data_form"):
        db_level = st.number_input('dB Level', min_value=0, step=1)
        current_datetime = datetime.now()
        years = [current_datetime.year, current_datetime.year + 1]
        months = list(range(1, 13))
        days = list(range(1, 32))
        hours = [f"{i if i != 0 else 12}{' AM' if i < 12 else ' PM'}" for i in range(24)]

        year = st.selectbox('Year', years)
        month = st.selectbox('Month', months)
        day = st.selectbox('Day', days)
        hour = st.selectbox('Hour', hours)

        minute = st.number_input('Minute', min_value=0, max_value=59, step=1)
        hour = int(hour.split()[0]) + (12 if "PM" in hour and hour.split()[0] != '12' else 0) - (12 if "AM" in hour and hour.split()[0] == '12' else 0)
        timestamp = datetime(year, month, day, hour, minute).strftime('%Y-%m-%d %H:%M:%S')
        location = st.text_input('Location')
        comments = st.text_area('Comments')
        submit_button = st.form_submit_button("Add to Spreadsheet")

        if 'noise_data' not in st.session_state:
            st.session_state.noise_data = []
        
        if submit_button:
            st.session_state.noise_data.append({
                "dB Level": db_level,
                "Timestamp": timestamp,
                "Location": location,
                "Comments": comments
            })

    # Upload and selectively add data to session
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.session_state.uploaded_data = df.to_dict('records')  # Temporarily hold data for review

    if 'uploaded_data' in st.session_state:
        st.subheader("Select data to add:")
        selected_indices = st.multiselect("Select entries:", options=range(len(st.session_state.uploaded_data)),
                                          format_func=lambda x: f"{st.session_state.uploaded_data[x]['Timestamp']} - {st.session_state.uploaded_data[x]['dB Level']} dB")
        if st.button("Add selected data to current session"):
            selected_data = [st.session_state.uploaded_data[i] for i in selected_indices]
            st.session_state.noise_data.extend(selected_data)
            del st.session_state.uploaded_data  # Clear uploaded data after adding

    # Display and manage current data entries
    if st.session_state.noise_data:
        st.write("Current Data Entries:")
        for i in range(len(st.session_state.noise_data)):
            entry = st.session_state.noise_data[i]
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.write(f"{i+1}. {entry['dB Level']} dB, {entry['Timestamp']}, {entry['Location']}, {entry['Comments']}")
            with col2:
                if st.button("X", key=f"delete_{i}"):
                    st.session_state.noise_data.pop(i)
                    st.experimental_rerun()

    if st.button('Create Spreadsheet', key='create_spreadsheet_button'):
        if st.session_state.noise_data:
            spreadsheet_content = create_spreadsheet(st.session_state.noise_data)
            st.text_area("Generated Spreadsheet:", spreadsheet_content, height=300)
            st.download_button(
                label="Download Spreadsheet as CSV",
                data=spreadsheet_content,
                file_name='noise_data.csv',
                mime='text/csv',
            )

            # Record audio when creating spreadsheet
            record_audio("output.wav", duration=5)

import plotly.express as px

def create_spreadsheet(noise_data):
    # Construct the prompt for the OpenAI API
    prompt_text = "Create a CSV format with the columns: dB Level, Timestamp, Location, Comments. Here is the data:\n\n"
    for entry in noise_data:
        # Properly format the prompt to handle potential commas in the comments
        comments = str(entry.get('Comments', '')).replace(',', ';')
        prompt_text += f"{entry['dB Level']}, {entry['Timestamp']}, {entry['Location']}, \"{comments}\"\n"
    
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt_text,
        temperature=0.5,
        max_tokens=200,
        top_p=1
    )
    # Extract the formatted spreadsheet content from the response
    spreadsheet_content = response.choices[0].text
    
    # Convert the spreadsheet content to a pandas DataFrame
    df = pd.read_csv(io.StringIO(spreadsheet_content))
    
    # Graph the data using plotly
    fig = px.scatter(df, x='Timestamp', y='dB Level', color='Location')
    st.plotly_chart(fig)
    
    return spreadsheet_content

if __name__ == "__main__":
    main()
