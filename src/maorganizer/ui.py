import io
import types
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import pandas as pd
import streamlit as st

from maorganizer.datawrangling import (
    CSV_EXTENSIONS,
    EXCEL_EXTENSIONS,
    NAMECOLUMN,
    Attendancelist,
)

ACCEPTED_EXTENSIONS = CSV_EXTENSIONS + EXCEL_EXTENSIONS

SEPARATORTYPES = {"TAB": "\t", "COMMA": ","}


@dataclass
class Task:
    abbreviation: str
    short_description: str
    long_description: str
    run: types.FunctionType


@dataclass
class Tasks:
    tasks: list[Task]

    def __post_init__(self):
        assert len(self.abbreviations) == len(set(self.abbreviations))
        assert len(self.short_descriptions) == len(set(self.abbreviations))

    @property
    def abbreviations(self):
        return [task.abbreviation for task in self.tasks]

    @property
    def short_descriptions(self):
        return [task.short_description for task in self.tasks]


def split_names(meetings: Dict[str, Attendancelist]) -> None:
    filename = st.selectbox(
        "Choose a file 📄", options=list(meetings.keys()), key="split_names"
    )

    render_xlsx_download_button(
        {"Full list of Attendees": meetings[filename]},
        filename=f"processed-attendees-{Path(filename).stem}.xlsx",
    )


def find_attendees(meetings: Dict[str, Attendancelist]) -> None:
    def _render_findings(to_be_found, people_found):
        st.subheader(f"**{to_be_found}**")
        st.markdown(
            f"{', '.join([p.name for p in people_found]) if people_found else 'Sorry, none found.'}"
        )

    filename = st.selectbox(
        "📄 Choose a file", options=list(meetings.keys()), key="find_attendees"
    )
    attendees = meetings[filename]

    textinput = st.text_input(
        "🔎 Who are you looking for? If you are looking for more than one, separate them by comma."
    )
    if textinput:
        searchterms = [(word.strip()) for word in textinput.strip().split(",")]
    else:
        searchterms = []

    st.markdown(
        "⚠️ By default, the algorithm will surface any names that contain your search terms"
        " as substrings (e.g. if you search for Jon, it will surface both Jon and Jonathan)."
        " Tick the box below in case you want to display only entries where one of the names"
        " matches your search string exactly."
    )
    st.markdown("⚠️⚠️ Note that either way the search is case-insensitive.")
    exact_match = st.checkbox("Find Exact Name")

    if searchterms:
        st.header("Search Results")

        for to_be_found, found in attendees.find_by_strings(
            searchterms, exact=exact_match
        ).items():
            _render_findings(to_be_found, found)


def compare_meetings(meetings: Dict[str, Attendancelist]) -> None:
    col1, col2 = st.columns(2)
    with col1:
        filename_old = st.selectbox(
            "Choose your original file", options=list(meetings.keys())
        )
    with col2:
        filename_new = st.selectbox(
            "Choose your updated file", options=set(meetings.keys()) - {filename_old}
        )

    # filename_new gets automatically populated if there is more than one file
    # so if there is none, it's because there is only a single file available
    # and no options left for filename_new
    if filename_new is None:
        st.info("⬆ Please upload a second file. ⬆")
    else:
        listcomparison = {
            "Original List": meetings[filename_old],
            "Updated List - Full": meetings[filename_new],
            "Updated List - Only Updates": meetings[filename_old].update(
                meetings[filename_new]
            ),
        }

        render_xlsx_download_button(
            listcomparison,
            filename=f"{Path(filename_old).stem}-updated.xlsx",
        )


def create_tasks() -> Tasks:
    return Tasks(
        [
            Task(
                abbreviation="SPLIT",
                short_description=(
                    "✂️ ... split attendees into first"
                    "and last name and download results"
                ),
                long_description=(
                    "❔ **Description:** Split a list of names"
                    " into first and surname."
                ),
                run=split_names,
            ),
            Task(
                abbreviation="COMPARE",
                short_description=" 👀 ... compare two meetings with each other and find updates",
                long_description=(
                    "❔ **Description:** Compare two attendee lists"
                    " with each and find attendees who have recently joined."
                ),
                run=compare_meetings,
            ),
            Task(
                abbreviation="FIND",
                short_description=" 🔎 ... find specific attendees",
                long_description=(
                    "❔ **Description:** Find attendees in a list"
                    " by either first name or surname or by substrings."
                ),
                run=find_attendees,
            ),
        ]
    )


def render_xlsx_download_button(
    meetings: Dict[str, Attendancelist], filename: str
) -> None:
    with io.BytesIO() as output:
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            for sheetname, attendees in meetings.items():
                attendees.to_df().to_excel(writer, sheet_name=sheetname, index=False)

        st.download_button(
            label="💾 Download Results",
            data=output.getvalue(),
            file_name=filename,
            mime="application/vnd.ms-excel",
        )


def select_task(tasks: Tasks) -> Task:
    selected_task = st.radio("I would like to ...", tasks.short_descriptions)

    for task in tasks.tasks:
        if task.short_description == selected_task:
            st.markdown(task.long_description)
            break

    return task


def render_file_analysis(meetings: Dict[str, Attendancelist]) -> None:
    show_processed_list = st.checkbox("Display the processed list of attendees")
    if show_processed_list:
        filename = st.selectbox(
            "Select the file to display", options=list(meetings.keys())
        )
        attendees = meetings[filename]

        st.write(attendees.to_df())


def load_data(uploaded_files) -> Dict[str, Attendancelist]:
    def _files_contain_csv(uploaded_files) -> bool:
        return bool(
            sum([Path(file.name).suffix in CSV_EXTENSIONS for file in uploaded_files])
        )

    def _load_df_from_uploaded_data(filename: str, data, sep=None) -> pd.DataFrame:
        if Path(filename).suffix in EXCEL_EXTENSIONS:
            try:
                df = pd.read_excel(data)
            # If engine does not recognize excel as excel, it is likely to be
            # a text format "disguised" as xls.
            # (example: PyData Meeting files have .xls extension, but are in fact text files)
            except ValueError as e:
                if str(e) == (
                    "Excel file format cannot be determined,"
                    " you must specify an engine manually."
                ):
                    st.info(
                        f"Your {Path(filename).suffix} file does not seem"
                        " to be an excel file.\\\n\\\n"
                        "\- Trying to parse it as text file."
                    )
                    df = pd.read_csv(data, sep=sep)
                else:
                    raise ValueError(e)
        elif Path(filename).suffix in CSV_EXTENSIONS:
            df = pd.read_csv(data, sep=sep)
        else:
            raise ValueError(
                f"Please choose one of the following extensions: {', '.join(ACCEPTED_EXTENSIONS)}"
            )
        return df

    def _make_attendance_data_from_file_uploads(
        uploaded_files, sep=None, cname=NAMECOLUMN
    ) -> Dict[str, Attendancelist]:
        return {
            file.name: Attendancelist.from_df(
                _load_df_from_uploaded_data(file.name, file, sep), cname=cname
            )
            for file in uploaded_files
        }

    try:
        meetings = _make_attendance_data_from_file_uploads(
            uploaded_files, sep=None, cname=NAMECOLUMN
        )

    # let user specify file format, then retry loading
    # Retry parsing after letting user manually specify separator and columnname.
    # Display error **after** the input fields, so if manually specifying separator and columnname
    # fixes the load issue, the error message disappears.
    except KeyError:
        # Set separator if csv file present
        if _files_contain_csv(uploaded_files):
            seperator_key = st.radio(
                "We detected text files in your input. What is their separator?",
                sorted(SEPARATORTYPES.keys()),
            )
            separator = SEPARATORTYPES[seperator_key]
        else:
            separator = None

        # Set columnname
        columnname = st.text_input(
            "Column header of your file's name column", NAMECOLUMN
        )

        try:
            meetings = _make_attendance_data_from_file_uploads(
                uploaded_files, sep=separator, cname=columnname
            )
        except KeyError:
            st.error(
                f'We could not find a column "{columnname}" in your data.\\\n\\\n'
                " Please use the options above to specify your column separator (if text/csv file)"
                " and the column name of the column containing your attendees' names."
            )
            meetings = {}

    if meetings:
        st.success(
            "Successfully loaded the following files:\\\n\\\n"
            + "\\\n".join(
                [f"{k} - {v.n_attendees} attendees" for k, v in meetings.items()]
            )
        )
    return meetings


def upload_files() -> Dict[str, Attendancelist]:
    st.markdown(
        "Upload the file(s) containing your meeting attendees. The expected format is a single"
        " column containing the attendees' full names. If you column name is not Name,"
        " you will be able to specify the column name after uploading the data."
        " Additional columns will be ignored."
    )

    uploaded_files = st.file_uploader(
        label="📄 Upload your files", accept_multiple_files=True
    )

    meetings = {}
    if uploaded_files:
        meetings = load_data(uploaded_files)
        render_file_analysis(meetings)

    return meetings


def render_intro() -> None:
    st.title("📅 Meeting Attendance Organizer")
    st.markdown(
        "This app fullfills a simple need: Take a list of names of people"
        " attending a meeting and peform one (or multiple) of the following tasks:"
    )
    st.markdown(
        "* ✂️ Split their names into first name and surname\n"
        "* 👀 Compare two lists with each other and see who is new on the second list\n"
        "* 🔎 Find people in a list by either searching for their complete names or parts"
        " of their name\n"
        "* 💾 Write any of the results back out, so you can share it with others"
    )


def main():
    render_intro()

    st.header("📂 Step 1: Upload your Files")
    meetings = upload_files()

    st.header("📝 Step 2: Choose a Task")
    task = select_task(tasks=create_tasks())

    st.header("🔥 Step 3: Let's Go!")
    st.subheader(f"You are going to ... {task.short_description}")
    if not meetings:
        st.info("⬆ You need to upload some data first ⬆")
    else:
        task.run(meetings)


if __name__ == "__main__":
    main()
