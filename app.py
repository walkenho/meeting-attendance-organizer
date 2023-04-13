from pathlib import Path
import streamlit as st

from maorganizer.datawrangling import Person

from maorganizer.ui import TASKS, render_xlsx_download_button, create_file_uploader, create_task_selector

# all these beautiful emojis from https://emojidb.org/file-emojis

st.title("📅 Meeting Attendance Organizer")
st.markdown("This app fullfills a simple need: Take a list of names of people attending a meeting and peform one (or multiple) of the following tasks:")
st.markdown("""* ✂️ Split their names into first name and surname\n* 👀 Compare two lists with each other and see who is new on the second list\n * 🔎 Find people in a list by either searching for their complete names or parts of their name\n * 💾 Write any of the results back out, so you can share it with others""")

st.header("📂 Step 1: Upload your Files")
st.markdown("Upload the file(s) containing your meeting attendees. The expected format is a single column containing the attendees' full names. If you column name is not Name, you will be able to specify the column name after uploading the data. Additional columns will be ignored.")


meetings = {}
meetings = create_file_uploader()

task = create_task_selector()

st.header("🔥 Step 3: Let's Go!")
st.subheader(f"You are going to ... {task}")
if not meetings:
    st.info("⬆ You need to upload some data first ⬆") 

if meetings:
    if task == TASKS.SPLIT.value:

        filename = st.selectbox("Choose a file 📄", options=list(meetings.keys()), key=task)

        render_xlsx_download_button({'Full list of Attendees': meetings[filename]},
                                      filename=f"processed-attendees-{Path(filename).stem}.xlsx",
                                      key=TASKS.SPLIT.value+'download')

    elif task == TASKS.FIND.value:

        filename = st.selectbox("📄 Choose a file", options=list(meetings.keys()), key=task)
        attendees = meetings[filename]
        
        textinput = st.text_input("🔎 Who are you looking for? If you are looking for more than one, separate them by comma.")
        st.markdown("⚠️ By default, the algorithm will surface any names that contain your search terms as substrings (e.g. if you search for Jon, it will surface both Jon and Jonathan). Tick the box below in case you want to display only entries where one of the names matches your search string exactly.")
        st.markdown("⚠️⚠️ Note that either way the search is case-insensitive.")
        exact_match = st.checkbox("Find Exact Name")

        if textinput.strip():
            st.header("Search Results")
            if exact_match:
                people_to_find = [Person(word.strip()) for word in textinput.split(',')]

                for to_find, found in attendees.find_people(people_to_find).items():
                    st.subheader(f"**{to_find.name}**")
                    st.markdown(f"{', '.join([p.name for p in found]) if found else 'Sorry, none found.'}")
            else:
                words_to_find = [word.strip() for word in textinput.split(',')]

                for word_to_find, people_found in attendees.find_words(words_to_find).items():
                    st.subheader(f"**{word_to_find}**")
                    st.markdown(f"{', '.join([p.name for p in people_found]) if people_found else 'Sorry, none found.'}")

    elif task == TASKS.COMPARE.value:
        col1, col2 = st.columns(2)
        with col1:
            filename_old = st.selectbox("Choose your original file", options=list(meetings.keys()), key=task)
        with col2:
            filename_new = st.selectbox("Choose your updated file", options=set(meetings.keys()) - {filename_old})

        # filename_new gets automatically populated if there is more than one file
        # so if there is none, it's because there is only a single file available and no options left for filename_new
        if filename_new is None:
            st.info("⬆ Please upload a second file. ⬆")
        else:
            listcomparison = (
            {'Original List': meetings[filename_old],
             'Updated List - Full': meetings[filename_new],
             'Updated List - Only Updates': meetings[filename_old].update(meetings[filename_new])})

            render_xlsx_download_button(listcomparison, filename=f"{Path(filename_old).stem}-updated.xlsx", key=TASKS.COMPARE.value+'download')