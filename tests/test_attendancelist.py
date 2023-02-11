from maorganizer.datawrangling import Person, Attendancelist


def test_attendancelist_finds_person_by_substring():
    assert Attendancelist({Person("zaphod beeblebrox"), Person("ford prefix")}).find(
        Person("zaphod")
    ) == {Person("Zaphod Beeblebrox")}


def test_attendancelists_finds_multiple_people_if_existent():
    assert Attendancelist(
        {Person("zaphod beeblebrox"), Person("zaphod prefix"), Person("ford prefix")}
    ).find(Person("zaphod")) == {Person("Zaphod Beeblebrox"), Person("Zaphod Prefix")}


def test_find_multiple_finds_alls():
    assert Attendancelist(
        {Person("zaphod beeblebrox"), Person("ford prefix"), Person("Marvin")}
    ).find_multiple({Person("zaphod"), Person("ford prefix")}) == {
        Person(name="Ford Prefix"): {Person(name="Ford Prefix")},
        Person(name="Zaphod"): {Person(name="Zaphod Beeblebrox")},
    }

def test_attendance_list_updates_correctly():
    assert Attendancelist({Person('zaphod beeblebrox'), Person('ford prefix')}).update(Attendancelist({Person('zaphod beeblebrox'), Person('ford prefix'), Person('lord crawfish')})) == Attendancelist(participants={Person('lord crawfish')})