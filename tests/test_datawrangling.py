import pytest

from maorganizer.datawrangling import Person


def test_Person_parses_name_correctly():
    assert Person("Zaphod Beeblebrox").name == "Zaphod Beeblebrox"


def test_Person_name_gets_capitalized_correctly():
    assert Person("zaphod beeblebrox").name == "Zaphod Beeblebrox"


@pytest.mark.parametrize(
    "name,firstname",
    [
        ("Zaphod", "Zaphod"),
        ("Zaphod Beeblebrox", "Zaphod"),
        ("Zaphod Lucius Beeblebrox", "Zaphod"),
    ],
)
def test__Person_firstname_is_extracted_correctly(name, firstname):
    assert Person(name).firstname == firstname


@pytest.mark.parametrize(
    "name,lastname",
    [
        ("zaphod", ""),
        ("Zaphod Beeblebrox", "Beeblebrox"),
        ("Zaphod Lucius Beeblebrox", "Lucius Beeblebrox"),
    ],
)
def test_Person_lastname_is_extracted_correctly(name, lastname):
    assert Person(name).lastname == lastname


def test_whitespace_gets_deleted_from_edges_of_name():
    assert Person(" zaphod beeblebrox ") == Person("zaphod beeblebrox")


def test_multiple_whitespace_gets_correctly_deleted_from_inside_a_name():
    assert Person("Zaphod  Beeblebrox") == Person("Zaphod Beeblebrox")
