import streamlit as st
from enum import Enum

from maorganizer.datawrangling import Attendancelist, Person

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
    #st.markdown("## Upload your Attendee List")
    separator = st.radio("What's your input file separator?", SEPARATORTYPES.keys())

    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        attendees = Attendancelist.load_from_file(uploaded_file, sep=SEPARATORTYPES.get(separator))

        st.info(f"INFO: Your event has {attendees.n_attendees}.")

        show_processed_list = st.checkbox("Show me the processed list of attendees")
        if show_processed_list:
            st.write(attendees.to_df())

        st.download_button("Press to Download Results",
                           attendees.to_file(),
                           f"processed-attendees-{uploaded_file.name}",
                           "text/csv",
                           key='download-csv')

if task == TASKS.TASK1.value:

    separator = st.radio("What's your input file separator?", SEPARATORTYPES.keys())

    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        attendees = Attendancelist.load_from_file(uploaded_file, sep=SEPARATORTYPES.get(separator))

        show_processed_list = st.checkbox("Show me the processed list of attendees")
        if show_processed_list:
            st.write(attendees.to_df())

        textinput = st.text_input("Who are you looking for? If you are looking for more than one, separate them by comma.")
        if textinput.strip():
            people_to_find = [Person(attendee.strip()) for attendee in textinput.split(',')]

            st.header("Search Results")
            for k, v in attendees.find_multiple(people_to_find).items():
                st.subheader(f"**{k.name}**")
                st.markdown(f"{', '.join([a.name for a in v]) if v else 'Sorry, none found.'}")