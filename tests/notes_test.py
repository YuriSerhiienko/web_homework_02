import pymakers.classes_for_notebook as notes
import pytest


def test_add_note():
    note_1 = notes.Note(("hello my friends!"))
    note_2 = notes.Note("buy some bread")
    note_3 = notes.Note("call Mary")
    note_4 = "celebrate birthday"
    hashtag_1 = notes.Hashtag("#hello")
    hashtag_2 = notes.Hashtag("#buy")
    hashtag_3 = notes.Hashtag("#call")
    hashtag_4 = notes.Hashtag("#birthaday")
    record_1 = notes.RecordNote(hashtag_1, note_1)
    record_2 = notes.RecordNote(hashtag_2, note_2)

    record_1.add_note("hello others")
    record_2.add_note(notes.Note("buy milk"))
    assert len(record_1.notes) == 2
    assert len(record_2.notes) == 2
    with pytest.raises(ValueError):
        record_2.add_note(123)


def test_edit_note():
    note_1 = notes.Note("hello my friends!")
    note_2 = notes.Note("hello others")
    note_3 = notes.Note("hello mom")
    hashtag_1 = notes.Hashtag("#hello")

    record_1 = notes.RecordNote(hashtag_1, note_1)
    record_1.add_note(note_2)
    record_1.edit_note(note_2.value, note_3.value)
    assert record_1.notes[1].value == "hello mom"
    record_1.edit_note(note_1.value, "hello dad")
    assert record_1.notes[0].value == "hello dad"


def test_show():
    note_1 = notes.Note("hello my friends!")
    note_2 = notes.Note("hello others")
    note_3 = notes.Note("hello mom")
    hashtag_1 = notes.Hashtag("#hello")
    record_1 = notes.RecordNote(hashtag_1, note_1)
    record_1.add_note(note_2)
    record_1.add_note(note_3)
    assert record_1.show() == ["hello my friends!", "hello others", "hello mom"]


def test_get_hashtag():
    note_1 = notes.Note("hello my friends!")
    note_2 = notes.Note("buy some bread")
    note_3 = notes.Note("call Mary")
    note_4 = "celebrate birthday"
    hashtag_1 = notes.Hashtag("#hello")
    hashtag_4 = notes.Hashtag("#birthday")
    record_1 = notes.RecordNote(hashtag_1, note_1)
    record_2 = notes.RecordNote("#buy", note_2)
    record_4 = notes.RecordNote(hashtag_4, note_4)
    assert record_1.get_hashtag() == "#hello"
    assert record_2.get_hashtag() == "#buy"
    assert record_4.get_hashtag() == "#birthday"


def test_get_note_by_index():
    note_1 = notes.Note("hello my friends!")
    note_2 = notes.Note("buy some bread")
    note_3 = notes.Note("call Mary")
    note_4 = "celebrate birthday"
    hashtag_1 = notes.Hashtag("#hello")
    hashtag_4 = notes.Hashtag("#birthday")
    record_1 = notes.RecordNote(hashtag_1, note_1)
    record_1.add_note(note_2)
    record_1.add_note(note_3)
    record_1.add_note(note_4)
    assert record_1.get_note_by_index(2) == "call Mary"
    with pytest.raises(IndexError):
        record_1.get_note_by_index(4)


def test_str():
    note_1 = notes.Note("hello my friends!")
    note_2 = notes.Note("hello mom")
    note_3 = notes.Note("hello dad")
    note_4 = "hello dude"
    hashtag_1 = notes.Hashtag("#hello")
    hashtag_4 = notes.Hashtag("#birthday")
    record_1 = notes.RecordNote(hashtag_1, note_1)
    record_1.add_note(note_2)
    record_1.add_note(note_3)
    record_1.add_note(note_4)
    assert (
        record_1.__str__()
        == "#hello: hello my friends!, hello mom, hello dad, hello dude"
    )


def test_repr():
    note_1 = notes.Note("hello my friends!")
    note_2 = notes.Note("hello mom")
    note_3 = notes.Note("hello dad")
    note_4 = "hello dude"
    hashtag_1 = notes.Hashtag("#hello")
    hashtag_4 = notes.Hashtag("#birthday")
    record_1 = notes.RecordNote(hashtag_1, note_1)
    record_1.add_note(note_2)
    record_1.add_note(note_3)
    record_1.add_note(note_4)
    assert (
        record_1.__repr__()
        == "Record(#hello, hello my friends!, hello mom, hello dad, hello dude)"
    )


def test_add_record():
    notebook = notes.Notebook()
    note_1 = notes.Note("hello my friends!")
    note_2 = notes.Note("hello mom")
    note_3 = notes.Note("celebrate birthday")
    hashtag_1 = notes.Hashtag("#hello")
    hashtag_2 = notes.Hashtag("#birthday")
    record_3 = notes.RecordNote(hashtag_2, note_3)
    notebook.add_record(notes.RecordNote(hashtag_1, note_1))
    assert repr(notebook.get(hashtag_1.value)) == "Record(#hello, hello my friends!)"
