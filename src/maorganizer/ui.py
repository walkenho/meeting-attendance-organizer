import io
from enum import Enum
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd
import streamlit as st

from maorganizer.datawrangling import NAMECOLUMN, Attendancelist

CSV_EXTENSIONS = [".csv", ".txt"]
EXCEL_EXTENSIONS = [".xls", ".xlsx"]
ACCEPTED_EXTENSIONS = CSV_EXTENSIONS + EXCEL_EXTENSIONS


SEPARATORTYPES = {"TAB": "\t", "COMMA": ","}


class TASKS(str, Enum):
    SPLIT = "✂️ ... split attendees into first and last name and download results"
    COMPARE = " 👀 ... compare two meetings with each other and find updates"
    FIND = " 🔎 ... find specific attendees"

    def __str__(self) -> str:  # makes enum values duck-type to strings
        return str.__str__(self)


def load_df_from_uploaded_data(filename, data, sep=None) -> pd.DataFrame:
    if Path(filename).suffix in EXCEL_EXTENSIONS:
        df = pd.read_excel(data)
    elif Path(filename).suffix in CSV_EXTENSIONS:
        df = pd.read_csv(filename, sep=sep)
    else:
        raise ValueError(
            f"Please choose one of the following extensions: {', '.join(ACCEPTED_EXTENSIONS)}"
        )
    return df


def make_attendance_data_from_file_uploads(
    uploaded_files, sep=None, cname=NAMECOLUMN
) -> Dict:
    return {
        file.name: Attendancelist.load_from_df(
            load_df_from_uploaded_data(file.name, file, sep), cname=cname
        )
        for file in uploaded_files
    }


def load_data(uploaded_files) -> Tuple[Dict, bool]:
    try:
        data = make_attendance_data_from_file_uploads(
            uploaded_files, sep=None, cname=NAMECOLUMN
        )
    except KeyError:
        contains_csvs = sum(
            [Path(file.name).suffix in CSV_EXTENSIONS for file in uploaded_files]
        )
        if contains_csvs:
            separator = st.radio(
                "We detected text files in your input. What is their separator?",
                sorted(SEPARATORTYPES.keys()),
            )

        namecolumn = st.text_input(
            "Column header of your file's name column", NAMECOLUMN
        )
        try:
            data = make_attendance_data_from_file_uploads(
                uploaded_files, sep=SEPARATORTYPES[separator], cname=namecolumn
            )
        except KeyError:
            st.error(
                f"We could not find a column {namecolumn} in your data. Please use the options above to specify your column separator and the column name of your name column."
            )
            data = {}

    if data:
        st.success(
            "Successfully loaded the following files:\\\n\\\n"
            + "\\\n".join([f"{k} - {v.n_attendees} attendees" for k, v in data.items()])
        )
    return data


def render_file_selector(meetings, key):
    show_processed_list = st.checkbox("Display the processed list of attendees")
    if show_processed_list:
        filename = st.selectbox(
            "Select the file to display", options=list(meetings.keys()), key=key
        )
        attendees = meetings[filename]

        st.write(attendees.to_df())


def create_file_uploader():
    uploaded_files = st.file_uploader(
        label="📄 Upload your files", accept_multiple_files=True
    )
    if uploaded_files:
        meetings = load_data(uploaded_files)
        render_file_selector(meetings, "file_upload")
        return meetings
    else:
        return {}


def create_task_selector():
    st.header("📝 Step 2: Choose a Task")
    task = st.radio("I would like to ...", [task.value for task in TASKS])

    if task == TASKS.SPLIT.value:
        st.markdown("❔ **Description:** Split a list of names into first and surname.")
    elif task == TASKS.COMPARE.value:
        st.markdown(
            "❔ **Description:** Compare two attendee lists with each and find attendees who have recently joined."
        )
    elif task == TASKS.FIND.value:
        st.markdown(
            "❔ **Description:** Find attendees in a list by either first name or surname or by substrings."
        )
    return task


def render_xlsx_download_button(data, filename, key) -> None:
    with io.BytesIO() as output:
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            for sheetname, attendees in data.items():
                attendees.to_df().to_excel(writer, sheet_name=sheetname, index=False)
            writer.save()

        st.download_button(
            label="💾 Download Results",
            data=output.getvalue(),
            file_name=filename,
            mime="application/vnd.ms-excel",
            key=key,
        )
