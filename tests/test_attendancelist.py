from maorganizer.datawrangling import Attendancelist, Person


def test_attendancelist_finds_person_by_substring():
    assert Attendancelist(
        {Person("zaphod beeblebrox"), Person("ford prefix")}
    ).find_word("aph") == {Person("Zaphod Beeblebrox")}


def test_attendancelist_finds_person_by_namepart():
    assert Attendancelist(
        {Person("zaphod beeblebrox"), Person("ford prefix")}
    ).find_person(Person("zaphod")) == {Person("Zaphod Beeblebrox")}


def test_attendancelists_finds_multiple_people_if_existent():
    assert Attendancelist(
        {Person("zaphod beeblebrox"), Person("zaphod prefix"), Person("ford prefix")}
    ).find_person(Person("zaphod")) == {
        Person("Zaphod Beeblebrox"),
        Person("Zaphod Prefix"),
    }


def test_find_people_finds_alls():
    assert Attendancelist(
        {Person("zaphod beeblebrox"), Person("ford prefix"), Person("Marvin")}
    ).find_people({Person("zaphod"), Person("ford prefix")}) == {
        Person(name="Ford Prefix"): {Person(name="Ford Prefix")},
        Person(name="Zaphod"): {Person(name="Zaphod Beeblebrox")},
    }


def test_attendance_list_updates_correctly():
    assert Attendancelist({Person("zaphod beeblebrox"), Person("ford prefix")}).update(
        Attendancelist(
            {
                Person("zaphod beeblebrox"),
                Person("ford prefix"),
                Person("lord crawfish"),
            }
        )
    ) == Attendancelist(participants={Person("lord crawfish")})


def test_attendancelist_has_correct_n_attendees():
    assert (
        Attendancelist({Person("zaphod beeblebrox"), Person("ford prefix")}).n_attendees
        == 2
    )
