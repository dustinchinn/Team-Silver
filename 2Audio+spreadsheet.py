import streamlit as st
import pandas as pd
from datetime import datetime, time as datetime_time
import pyaudio
import numpy as np
import time
import os
import requests

def calculate_dbs(data, sample_rate):
    rms = np.sqrt(np.mean(data ** 2))
    db_level = 20 * np.log10(rms)
    return db_level

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
    """Appends a list of data entries (each a dictionary) to a CSV file, with headers if the file does not exist."""
    import pandas as pd
    import os

    if not os.path.isfile(filename) or os.stat(filename).st_size == 0:
        # File does not exist or is empty, initialize it with headers from the first data entry
        pd.DataFrame(data_list).to_csv(filename, index=False)
    else:
        # File exists, append data without writing headers
        current_df = pd.read_csv(filename)
        new_df = pd.DataFrame(data_list)
        next_order_number = len(current_df) + 1
        new_df['Order Number'] = range(next_order_number, next_order_number + len(new_df))
        cols = ['Order Number'] + [col for col in new_df.columns if col != 'Order Number']
        new_df = new_df[cols]
        new_df.to_csv(filename, mode='a', header=False, index=False)

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
    st.title('Noise Data Recorder and Spreadsheet Creator')
    st.info("Please enter the details and click 'Record' to start recording for 5 seconds.")

    if "noise_data" not in st.session_state:
        st.session_state.noise_data = []
    
    if 'category' not in st.session_state:
        st.session_state['category'] = None  # Initialize session state for category

    with st.form("noise_data_form"):
        col1, col2 = st.columns(2)
        with col1:
            # User can edit the date
            date = st.date_input("Date", datetime.now())
        with col2:
            # User can edit the time, combining hours and minutes into a single line
            current_time = datetime.now()
            hours = range(1, 13)
            minutes = range(0, 60)
            time_options = [f"{hour}:{minute:02d} {'AM' if current_time.hour < 12 or current_time.hour == 24 else 'PM'}" for hour in hours for minute in minutes]
            selected_hour = current_time.hour if current_time.hour <= 12 else current_time.hour - 12
            current_time_index = (selected_hour - 1) * 60 + current_time.minute  # Adjust index for dropdown
            time_selection = st.selectbox("Time", time_options, index=current_time_index)

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
        hour_number = int(time_selection.split(':')[0])
        is_pm = time_selection.endswith('PM')
        if is_pm and hour_number != 12:
            hour_number += 12
        elif not is_pm and hour_number == 12:
            hour_number = 0

        timestamp = datetime.combine(date, datetime.min.time())
        timestamp = timestamp.replace(hour=hour_number, minute=int(time_selection.split(':')[1][:2]))
        timestamp_str = timestamp.strftime('%m/%d/%Y %H:%M')

        # Create a placeholder for the message
        message = st.empty()
        message.info("Recording started. Please wait for 5 seconds.")
        db_level = record_audio(duration=5)
    
        # Update the message in the placeholder
        message.success("Recording successful and data recorded.")

        # Append the data to session state
        st.session_state.noise_data.append({
            "dB Level": db_level,
            "Timestamp": timestamp_str,
            "Location": location_input,
            "Category": category,
            "Comments": comments
        })

    # Display and manage current data entries
    if st.session_state.noise_data:
        st.write("Current Data Entries:")
        st.info("Click 'X' to delete an entry. Then click 'Report' when you are done recording all the data.")
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
    

if __name__ == "__main__":
    main()
