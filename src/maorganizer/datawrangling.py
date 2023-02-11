import pathlib
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set

import pandas as pd

DATAFOLDER = Path().cwd() / "data"

MONTH = "Feb"

FILENAME = f"participants-Meetup-{MONTH}"


@dataclass
class Person:
    name: str

    def __post_init__(self):
        self.name = self.name.title()

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


@dataclass
class Attendancelist:
    participants: Set[Person]

    def load_from_file(
        filename: pathlib.PosixPath, cname: str = "Name", sep: str = None
    ):
        if sep:
            df = pd.read_csv(filename, sep=sep)
        elif filename.suffix in [".xlsx", ".xls"]:
            df = pd.read_excel(filename)
        elif filename.suffix == ".csv":
            df = pd.read_csv(filename)
        else:
            raise ValueError(
                "Unsupported filetype, please specify a separator or choose one "
                "of the following filetypes: .xlsx, .xls, .csv"
            )

        return Attendancelist({Person(name) for name in df[cname]})

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
        return self.to_df().to_csv(index=False).encode('utf-8')

    def update(self, other: "Attendancelist"):
        return Attendancelist(other.participants - self.participants)

    def find(self, somebody: str):
        return {p for p in self.participants if p.is_similar(somebody)}

    def find_multiple(self, people: List[str]):
        return {p: self.find(p) for p in people}
