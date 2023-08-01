import pathlib
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set

import pandas as pd

CSV_EXTENSIONS = [".csv", ".txt"]
EXCEL_EXTENSIONS = [".xls", ".xlsx"]

DATAFOLDER = Path().cwd() / "data"

NAMECOLUMN = "Name"


@dataclass
class Person:
    name: str

    def __post_init__(self):
        self.name = " ".join(
            [namepart for namepart in self.name.strip().title().split(" ") if namepart]
        )

    def __hash__(self):
        return hash(self.name)

    def __equal__(self, other):
        return self.name == other.name

    def is_similar(self, other: "Person"):
        return (
            len(set(self.name.split(" ")).intersection(set(other.name.split(" ")))) != 0
        )

    @property
    def firstname(self):
        return self.name.split(" ")[0]

    @property
    def lastname(self):
        return " ".join(self.name.split(" ")[1:])

    def name_contains(self, text) -> bool:
        return text in self.name.lower()


@dataclass
class Attendancelist:
    participants: Set[Person]

    def from_df(df, cname: str = NAMECOLUMN):
        return Attendancelist({Person(name) for name in df[cname]})

    def from_file(
        filename: pathlib.PosixPath, cname: str = NAMECOLUMN, sep: str = None
    ):
        if filename.suffix in EXCEL_EXTENSIONS:
            df = pd.read_excel(filename)
        elif filename.suffix in CSV_EXTENSIONS:
            df = pd.read_csv(filename, sep=sep)
        else:
            raise ValueError(
                "Unsupported filetype, please specify a separator or choose one "
                f"of the following filetypes: {', '.join(EXCEL_EXTENSIONS+CSV_EXTENSIONS)}"
            )

        return Attendancelist.from_df(df, cname)

    @property
    def n_attendees(self):
        return len(self.participants)

    def to_df(self):
        return pd.DataFrame(
            [
                [participant.firstname, participant.lastname]
                for participant in self.participants
            ],
            columns=["firstname", "lastname"],
        ).sort_values(by="firstname")

    def save(self, filename: pathlib.PosixPath):
        if filename.suffix == ".xlsx":
            self.to_df().to_excel(filename, index=False)
        elif filename.suffix == ".csv":
            self.to_df().to_csv(filename, index=False)
        else:
            raise ValueError(
                "Unsupported filetype, please choose one of the following: .xlsx, .csv"
            )

    def to_file(self) -> str:
        return self.to_df().to_csv(index=False).encode("utf-8")

    def update(self, other: "Attendancelist"):
        return Attendancelist(other.participants - self.participants)

    def find_person(self, somebody: Person):
        return {p for p in self.participants if p.is_similar(somebody)}

    def find_people(self, people: List[Person]):
        return {p: self.find_person(p) for p in people}

    def find_by_string(self, word: str, exact=False):
        if exact:
            return self.find_person(Person(word))
        else:
            return {p for p in self.participants if p.name_contains(word.lower())}

    def find_by_strings(self, to_be_found: List[str], exact=False):
        return {tbf: self.find_by_string(tbf, exact=exact) for tbf in to_be_found}
