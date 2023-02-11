import streamlit as st
from enum import Enum

from maorganizer.datawrangling import Attendancelist

SEPARATORTYPES = {'TAB' : '\t', 'COMMA': ','}

class TASKS(str, Enum):
    TASK1 = "Split an attendee list into first and last name"
    TASK2 = "Compare two attendee lists with each other and find updates"
    TASK3 = "Search for specific attendees in my list"

    def __str__(self) -> str: # makes enum values duck-type to strings
        return str.__str__(self)
    

st.title("Welcome to the Meeting Attendance Organizer!")
task = st.radio("I would like to ...", [task.value for task in TASKS])

if task in (TASKS.TASK1.value, TASKS.TASK3.value):
    st.header("Upload your Attendee List")
    separator = st.radio("Input file separator", SEPARATORTYPES.keys())

    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        attendees = Attendancelist.load_from_file(uploaded_file, sep=SEPARATORTYPES.get(separator))

        st.write(f"Successfully processed {uploaded_file.name}.")
        st.write(f"Your event has {len(attendees)} attendees.")

        st.download_button("Press to Download Results",
                           attendees.to_file(),
                           f"attendees-{uploaded_file.name}",
                           "text/csv",
                           key='download-csv')
        st.write(attendees.to_df())