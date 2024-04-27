import streamlit as st
import pandas as pd
from datetime import datetime
import pyaudio
import numpy as np
import time
import os
import requests
from openai import OpenAI

client = OpenAI(api_key="Your API here")
# Create a wrapper function to get OpenAI completion
def get_completion(prompt, model="gpt-3.5-turbo"):
    completion = client.chat.completions.create(
        model=model,
        messages=[
        {"role": "system", "content": 'You are a helpful chatbot. Thank the user for their report, then provide a suggestion based on their prompt. Including this "Still have questions? Please click the "Chat" button below."'},
        {"role": "user", "content": prompt},
        ]
    )
    return completion.choices[0].message.content
#Calculate a dB level from audio data
def calculate_dbs(data, sample_rate):
    rms = np.sqrt(np.mean(data ** 2))
    db_level = 20 * np.log10(rms)
    return db_level
#Record audio using PyAudio
def record_audio(duration=5, sample_rate=44100, channels=1, format=pyaudio.paInt16):
    p = pyaudio.PyAudio()
    stream = p.open(format=format,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=1024)

    frames = []
    for i in range(0, int(sample_rate / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)
        time.sleep(0.1)  # Reduce sleep time to keep UI responsive

    stream.stop_stream()
    stream.close()
    p.terminate()

    audio_data = b''.join(frames)
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    db_level = calculate_dbs(audio_array, sample_rate)

    return db_level

def append_to_csv(data_list, filename="noise_data.csv"):
    # Check if the file exists and is not empty
    if not os.path.isfile(filename) or os.stat(filename).st_size == 0:
        # If file doesn't exist or is empty, write with header and starting 'Entry' from 1
        with open(filename, 'w', newline='') as f:  # Ensure correct line handling on Windows
            pd.DataFrame([{'Entry': i + 1, **data} for i, data in enumerate(data_list)]).to_csv(f, index=False)
    else:
        # If file exists, read the current data to find the last 'Entry' number
        current_df = pd.read_csv(filename)
        max_entry = current_df['Entry'].max() if 'Entry' in current_df.columns else 0
        # Append new data with incremented 'Entry' numbers
        with open(filename, 'a', newline='') as f:  # Append mode, ensure correct line handling on Windows
            pd.DataFrame([{'Entry': max_entry + i + 1, **data} for i, data in enumerate(data_list)]).to_csv(f, header=False, index=False)

def get_location():
    try:
        response = requests.get('https://ipinfo.io/json')
        data = response.json()
        location = data.get('city') + ', ' + data.get('region') + ', ' + data.get('country')
        return location
    except Exception as e:
        st.error(f"Error retrieving location: {e}")
        return None

def main():
    st.title("Sound X - Noise Data Recorder")
    st.subheader("Welcome to Sound X, a tool to record and report noise data.", divider='grey')
    # Initialize agreement status in session state if not already present
    if 'agreed' not in st.session_state:
        st.session_state.agreed = False

    # Conditionally display the disclaimer and buttons based on agreement status
    if not st.session_state.agreed:
        # Display disclaimer using HTML for emphasis
        st.markdown(""" <div style='background-color: white; padding: 10px; border-radius: 5px;'>
                        <h2 style='color: red; text-align: center;'>Disclaimer</h2>
                        <p style='color: black; font-weight: bold;'>
                            By using this tool, you agree to allow this app to use your device's microphone and location 
                            to generate noise reports. This specific user data will <strong>not</strong> be distributed.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

        # Display Agree and Disagree buttons
        agree, disagree = st.columns(2)
        if agree.button("Agree"):
            st.session_state.agreed = True  # Update state to reflect agreement
            st.rerun()  # Force a rerun to refresh the page
        if disagree.button("Disagree"):
            st.error("You have chosen not to agree to the terms. Please close this tab or refresh to exit.")
            st.stop()  # Stop execution to prevent any further interaction

    # Display the rest of the application only if agreed
    if st.session_state.agreed:
        st.info("Please enter the details and click 'Record' to start recording.")
        st.subheader("Record Noise Data", divider='grey')
        with st.form("noise_data_form"):
            col1, col2 = st.columns(2)
            with col1:
                # Automatically capture the current date
                current_date = datetime.now().strftime('%m/%d/%Y')
                st.text(f"Date: {current_date}")
            with col2:
                # Automatically capture the current time
                current_time = datetime.now().strftime('%I:%M %p')
                st.text(f"Time: {current_time}")

            col1, col2 = st.columns(2)
            with col1:
                location = get_location()  # Fetch location using the defined function
                location_input = st.text_input('Location', value=location if location else 'Enter location manually')
            with col2:
                category_options = ["Loud music", "Construction", "Traffic", "Parties", "Animals / Pets", "Industrial machinery", "Airplanes", "Public transport", "Other (Please specify in comments)"]
                category = st.selectbox("Category", category_options)

            comments = st.text_area('Comments')
            record_button = st.form_submit_button("Record")

        if record_button:
            # Process after recording button is pressed
            process_recording(location_input, category, comments)

        # Display and manage current data entries
        display_current_data()


def process_recording(location_input, category, comments):
    current_date = datetime.now().strftime('%m/%d/%Y')
    current_time = datetime.now().strftime('%I:%M %p')
    timestamp_str = f"{current_date} {current_time}"
    # Placeholder for actual recording function
    with st.spinner('Recording in progress...'):
     db_level = record_audio(duration=5)
     st.success("Recording successful and data recorded.")

    
    # Append the data to session state
    st.session_state.noise_data.append({
        "dB Level": db_level,
        "Timestamp": timestamp_str,
        "Location": location_input,
        "Category": category,
        "Comments": comments
    })

def display_current_data():
    if "noise_data" not in st.session_state:
        st.session_state.noise_data = []
    if st.session_state.noise_data:
        st.info("Click the 'X' button to delete and record again if needed.")
        st.write("Current Data Entries:")
        for i, entry in enumerate(st.session_state.noise_data):
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.write(f"{i+1}. {entry['dB Level']} dB, {entry['Timestamp']}, {entry['Location']}, {entry['Category']}, {entry['Comments']}")
            with col2:
                if st.button("X", key=f"delete_{i}"):
                    st.session_state.noise_data.pop(i)
        if st.button('Report'):
            if st.session_state.noise_data:
                append_to_csv(st.session_state.noise_data)
                st.success("Data reported successfully and added to the central file.")
                st.session_state.noise_data = [] 
                prompt = f"{entry['dB Level']}\n{entry['Timestamp']}\n{entry['Location']}\n{entry['Category']}\n{entry['Comments']}"
    
                # Get the completion and overwrite the info message with the result
                completion = get_completion(prompt)

                # Display the completion
                st.success(completion)
            st.page_link("pages/testing.py", label="Chat", icon="💬")

if __name__ == "__main__":
    main()
    
