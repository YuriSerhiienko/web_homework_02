from pathlib import Path
from sort_dir import sort_dir
import pickle, re
from datetime import datetime
from collections import UserDict
from abc import ABC, abstractmethod

cashe = ""

class View(ABC):
    @abstractmethod
    def display_contacts(self, contacts):
        pass

    @abstractmethod
    def display_notes(self, notes):
        pass

    @abstractmethod
    def display_commands(self, commands):
        pass


class ConsoleView(View):
    def display_contacts(self, contacts):
        if not contacts:
            print("No contacts found.")
        else:
            for contact in contacts:
                print(contact)

    def display_notes(self, notes):
        if not notes:
            print("No notes found.")
        else:
            for note in notes:
                print(note)

    def display_commands(self, commands):
        print("Available commands:")
        for command in commands:
            print(command)


class Field:
    def __init__(self, value) -> None:
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value})"

class Hashtag(Field):
    def __init__(self, hashtag: str):
        super().__init__(hashtag)

    @Field.value.setter
    def value(self, hashtag):
        if hashtag[0] != "#":
            hashtag = "#" + hashtag
        if not re.match(r"^\#[\w\d]+$", hashtag):
            raise ValueError(
                "Hashtag value is not right it can be only alphabet letters (a-z), numbers (0-9) and _"
            )
        super(Hashtag, Hashtag).value.__set__(self, hashtag)

    def __repr__(self) -> str:
        return f"Hashtag({self.value})"

class Note(Field):
    def __init__(self, value):
        super().__init__(value)


class RecordNote:
    def __init__(self, hashtag, note=None):
        self.hashtag = hashtag
        self.notes = []
        if note is not None:
            self.add_note(note)

    def add_note(self, note):
        if isinstance(note, str):
            self.notes.append(Note(note))
        elif isinstance(note, Note):
            self.notes.append(note)
        else:
            raise ValueError("New note is not string value or Note() object")

    def edit_note(self, old_note, new_note):
        for note in self.notes:
            if note.value == old_note:
                note.value = new_note
                return note

    def show(self):
        result = []
        for note in self.notes:
            result.append(note.value)
        return result

    def get_hashtag(self):
        if isinstance(self.hashtag, Hashtag):
            return self.hashtag.value
        else:
            return self.hashtag

    def get_note_by_index(self, index):
        try:
            if self.notes:
                return self.notes[index].value
        except:
            raise IndexError

    def __str__(self):
        result = self.hashtag.value
        if self.notes:
            result += ": " + ", ".join([note.value for note in self.notes])
        return result

    def __repr__(self):
        if self.notes:
            notes_list=', '.join([note.value for note in self.notes])
            return f"Record({self.hashtag.value}, {notes_list})"


class Notebook(UserDict):
    def __init__(self, record=None):
        super().__init__()
        self.data = {}
        if record is not None:
            self.add_record(record)

    def add_record(self, record):
        self.data[record.get_hashtag()] = record

    def show(self):
        for hashtag, record in self.data.items():
            print(f"{hashtag}:")
            record.show()

    def display_notes(self, view):
        view.display_notes(self)

    def get_records(self, hashtag):
        return self.data.get(hashtag)

    def save_notes(self, filename):
        with open(filename, "wb") as file:
            pickle.dump(self.data, file)

    def load_notes(self, filename):
        try:
            with open(filename, "rb") as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            pass

    def search(self, value: str):
        result_by_note = []
        result_by_tag = []
        for tag, record in self.data.items():
            if value in tag:
                result_by_tag.append(record)
                continue
            for note in record.notes:
                if value in note.value:
                    result_by_note.append(record)
                    break
        return result_by_tag + result_by_note

    def __iter__(self):
        return iter(self.data.values())

    def __next__(self):
        if self._iter_index < len(self.data):
            record = list(self.data.values())[self._iter_index]
            self._iter_index += 1
            return record
        else:
            raise StopIteration

    def __str__(self):
        result = ""
        for tag in self.data:
            result += str(self.data[tag]) + "\n"
        return result

class Name(Field):
    def __init__(self, name: str):
        self.value = name

    @Field.value.setter
    def value(self, name):
        if not name.isalpha():
            raise ValueError("Give me name and phone/email/birthday please")
        Field.value.fset(self, name)

    def __repr__(self) -> str:
        return f"Name({self.value})"


class Phone(Field):

    def __init__(self, value) -> None:
        self.value = value

    @Field.value.setter
    def value(self, value:str):
        if value:
            number = re.sub(r'\D', '', value)
            if bool(re.search(r"^(38)?\d{10}$", number)) is not True:
                raise ValueError("Phone number is invalid! Look for the necessary format phone number in help.")
        Field.value.fset(self, number)
    
    def __repr__(self) -> str:
        return f"Phone({self.value})"


class Email(Field):
    def __init__(self, value) -> None:
        self.value = value

    @Field.value.setter
    def value(self, value:str):
        if value:            
            if bool(re.search(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", value)) is not True:
                raise ValueError("Email is invalid! Look for the necessary format email in help.")
        Field.value.fset(self, value)

    def __repr__(self) -> str:
        return f"Email({self.value})"


class Birthday(Field):
    def __init__(self, birthday):
        self.value = birthday

    @Field.value.setter
    def value(self, birthday):
        try:
            dt = datetime.strptime(birthday, '%d.%m.%Y')
        except (ValueError, TypeError):
            raise ValueError("Give me name and phone/email/birthday please")
        Field.value.fset(self, dt.date())

    def __repr__(self) -> str:
        return f"Birthday({self.value})"


class Record:
    def __init__(
        self,
        name: Name,
        phone: Phone | str | None = None,
        email: Email | str | None = None,
        birthday: Birthday | None = None
    ):
        self.name = name
        self.birthday = birthday

        self.phones = []
        if phone is not None:
            self.add_phone(phone)

        self.emails = []
        if email is not None:
            self.add_email(email)

    def add_phone(self, phone: Phone | str):
        if isinstance(phone, str):
            phone = self.create_phone(phone)
        self.phones.append(phone)

    def add_email(self, email: Email | str):
        if isinstance(email, str):
            email = self.create_email(email)
        self.emails.append(email)

    def add_birthday(self, birthday: Birthday | str):
        if isinstance(birthday, str):
            birthday = self.create_birthday(birthday)
        self.birthday = birthday

    def create_phone(self, phone: str):
        return Phone(phone)

    def create_email(self, email: str):
        return Email(email)

    def create_birthday(self, birthday: str):
        return Birthday(birthday)

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                return p

    def edit_email(self, old_email, new_email):
        for e in self.emails:
            if e.value == old_email:
                e.value = new_email
                return e

    def show(self):
        for inx, p in enumerate(self.phones):
            print(f'{inx}: {p.value}') 

    def get_phone(self, inx):
        if self.phones:
            return self.phones[inx]
        else:
            return None

    def get_name(self):
        return self.name.value

    def get_email(self, indx):
        if self.emails and indx < len(self.emails):
            return self.emails[indx]
        else:
            return None

    def get_birthday(self):
        return self.birthday

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.today().date()
            next_birthday = datetime(today.year, self.birthday.value.month, self.birthday.value.day).date()
            if today > next_birthday:
                next_birthday = datetime(today.year + 1, self.birthday.value.month, self.birthday.value.day).date()
            days_left = (next_birthday - today).days
            return days_left
        else:
            return "No birthday set"

    def __str__(self) -> str:
        return f"name: {self.name}: phones: {self.phones} emails: {self.emails} birthday: {self.birthday}"

    def __repr__(self) -> str:
        return f"Record({self.name!r}: {self.phones!r}, {self.emails!r}, {self.birthday!r})"


class AddressBook(UserDict):
    def __init__(self, record: Record | None = None) -> None:
        self.data = {}
        if record is not None:
            self.add_record(record)

    def add_record(self, record: Record):
        self.data[record.get_name()] = record

    def show(self):
        for name, record in self.data.items():
            print(f'{name}:')
            record.show()

    def display_contacts(self, view):
        view.display_contacts(self)

    def get_records(self, name: str) -> Record:
        try:
            return self.data[name]
        except KeyError:
            return None

    def save_address_book(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.data, file)

    def show_record(self, name: str) -> str:    
            result = ''
            record = self.get_records(name)
            result += f'{name}:'
            if record.phones:
                phones = ', '.join([phone.value for phone in record.phones])
                result += f' phones: {phones}'
            if record.emails:
                emails = ', '.join([email.value for email in record.emails])
                result += f' emails: {emails}'
            if record.birthday:
                result += f' birthday: {record.birthday.value}'
                days_left = record.days_to_birthday()
                result += f' days to birthday: {days_left}'
            return result

    def load_address_book(self, filename):
        try:
            with open(filename, 'rb') as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            pass

    def __iter__(self):
        return iter(self.data.values())

    def __next__(self):
        if self._iter_index < len(self.data):
            record = list(self.data.values())[self._iter_index]
            self._iter_index += 1
            return record
        else:
            raise StopIteration
        
def input_error(func):
    def inner(*args, **kwargs):
        global cashe
        try:
            result = func(*args, **kwargs)
            return result
        except KeyError:
            print(find_matching_lines(cashe))
            return "There is no such name"
        except ValueError as error:
            print(find_matching_lines(cashe))
            return str(error)
        except IndexError:
            print(find_matching_lines(cashe))
            return "Enter user name"
        except TypeError:
            print(find_matching_lines(cashe))
            return "Incorrect values"

    return inner


@input_error
def greeting():
    return "How can I help you?"


def unknown_command():
    return "Enter a new command"


def change_command(user_input):
    while True:
        print(find_matching_lines(user_input))
        choice = input(
            "Unknown command. Do you want to change the command? \n(Yes/No): "
        )

        if choice.lower() == "yes":
            words = user_input.split(" ")
            new_user_input = input("Repeat the command: ")
            if len(words) == 1:
                user_input = new_user_input + user_input[len(new_user_input) + 1 :]
            elif len(words) >= 2:
                user_input = " ".join([new_user_input] + words[1:])
            print(user_input)
            return user_input
        elif choice.lower() == "no":
            return None
        else:
            print('Please enter "Yes" or "No".')


@input_error
def exit():
    return None


def help():
    return (
        "add name 0*********/example@email.com/dd.mm.yyyy - add a phone/email/birthday to a contact\n"
        "note note_#hashtag_note - create a note with the specified hashtag(can be specified now or later)\n"
        "change name new_phone index - change the phone number at the specified index (if not specified, the first one will be changed)\n"
        "modify hashtag index new_note - modify the note with the specified hashtag and index\n"
        "search criteria - search for criteria among emails, phones, and names\n"
        "show all - show all contacts\n"
        "show notes - show all notes\n"
        "phone name - show all phone numbers for the specified name\n"
        "email name - show all emails for the specified name\n"
        "hashtag hashtag - displays all notes for the specified hashtag\n"
        "birthday name - show the birthday date with the number of days remaining\n"
        "birthdays - displays a list of contacts whose birthday is a specified number of days from the current date(standard 7 days)\n"\
        "page page_number number_of_contacts_per_page - show all contacts divided into pages, default is the first page with 3 contacts\n"
        "notes page_number number_of_hashtags - show all notes divided into pages, default is the first page with all notes of one hashtag\n"
        "delete name/#hashtag - clears a contact/hashtag by the specified name/hashtag\n"
        "exit/good bye/close - shutdown/end program"
    )


def find_matching_lines(user_input):
    matching_lines = []
    help_text = help()

    if user_input.strip():
        words = user_input.split()
        first_word = words[0]
        second_word = words[1] if len(words) > 1 else None

        for line in help_text.split("\n"):
            if first_word.lower() in line.lower() and len(first_word) >= 3:
                line = line.strip()
                if line:
                    matching_lines.append(line)

        if not matching_lines and second_word:
            for line in help_text.split("\n"):
                if second_word.lower() in line.lower() and len(second_word) >= 3:
                    line = line.strip()
                    if line:
                        matching_lines.append(line)

        if matching_lines:
            matching_lines.insert(0, "Commands in this context:")

    return "\n".join(matching_lines) + "\n"


@input_error
def add_user(name, contact_details):
    record = phonebook.get_records(name)
    if record:
        return update_user(record, contact_details)
    else:
        if "@" in contact_details:
            record = Record(Name(name), email=Email(contact_details))
        elif "." in contact_details:
            record = Record(Name(name), birthday=Birthday(contact_details))
        else:
            phone = Phone(contact_details)
            record = Record(Name(name), phone=phone)
        phonebook.add_record(record)
        return "Contact successfully added"


@input_error
def add_note(note):
    hashtags = extract_hashtags(note)

    if not hashtags:
        user_input = input("Please enter hashtags for the note: ")
        user_input = user_input.strip()
        if not user_input:
            hashtags = ["#untagged"]
        else:
            hashtags = extract_hashtags(user_input)
            if not hashtags:
                hashtags = [user_input]

    cleaned_note = remove_hashtags_from_note(note)

    for hashtag in hashtags:
        record = notebook.get_records(hashtag)
        if record:
            record.add_note(cleaned_note)
        else:
            record = RecordNote(Hashtag(hashtag), note=cleaned_note)
            notebook.add_record(record)

    return "Note added successfully"


def extract_hashtags(text):
    hashtags = []
    words = text.split()
    for word in words:
        if word.startswith("#"):
            hashtags.append(word)
    return hashtags


def remove_hashtags_from_note(note):
    cleaned_note = note
    hashtags = extract_hashtags(note)
    for hashtag in hashtags:
        cleaned_note = cleaned_note.replace(hashtag, "")
    cleaned_note = cleaned_note.strip()
    return cleaned_note


def update_user(record, contact_details):
    if "@" in contact_details:
        record.add_email(Email(contact_details))
    elif "." in contact_details:
        record.add_birthday(Birthday(contact_details))
    else:
        phone = Phone(contact_details)
        record.add_phone(phone)
    return "Contact details added successfully"


@input_error
def del_record(key: str):
    if "#" in key:
        notebook.data.pop(key)
        return f"Record for hashtag {key} was deleted from notebook."
    phonebook.data.pop(key)
    return f"Record for user {key} was deleted from addressbook."


@input_error
def change_phone(name, new_phone, index=0):
    record = phonebook.get_records(name)
    if record:
        if record.phones and "0" <= str(index) < str(len(record.phones)):
            record.edit_phone(
                old_phone=record.phones[int(index)].value, new_phone=new_phone
            )
            return "Phone number updated successfully"
        else:
            return "Invalid phone number index"
    else:
        return "There is no such name"


def change_note(hashtag, index, new_note):
    record = notebook.get_records(hashtag)
    if record:
        if record.notes and "0" <= str(index) < str(len(record.notes)):
            record.edit_note(old_note=record.notes[int(index)].value, new_note=new_note)
            return "Note updated successfully"
        else:
            return "Invalid note number index"
    else:
        return "There is no such hashtag"


@input_error
def show_all():
    if not phonebook.data:
        return "The phonebook is empty"
    result = ""
    for name in phonebook.data:
        result += phonebook.show_record(name) + "\n"
    return result.rstrip()


@input_error
def find_user_adressbook(name: str, flag=None):
    if not phonebook.data:
        return "The phonebook is empty"
    result = ""
    if flag is None:
        return phonebook.show_record(name)
    else:
        name = name.lower()
        for user in phonebook.data:
            if name == user.lower():
                result += phonebook.show_record(user) + "\n"
        return result.rstrip()


@input_error
def show_notes(criteria=None):
    if not notebook.data:
        return "The notebook is empty"
    if not criteria:
        return str(notebook)

    records = notebook.search(criteria)
    if not records:
        return "No note records found for " + criteria

    result = ""
    for record in records:
        result += str(record) + "\n"
    return result


@input_error
def get_note(hashtag):
    if hashtag[0] != "#":
        hashtag = "#" + hashtag
    record = notebook.get_records(hashtag)
    if record:
        notes = [f"{note}\n----------------------\n" for note in record.notes]
        if notes:
            notes_str = "".join(notes)
            return f"{hashtag}:\n{notes_str}"
        else:
            return f"No notes found for {hashtag}"
    else:
        return "There is no such hashtag"


@input_error
def get_birthday(name):
    record = phonebook.get_records(name)
    if record:
        if record.birthday:
            return f"{record.name.value}: {record.birthday.value}, Days to birthday: {record.days_to_birthday()}"
        else:
            return "No birthday found for that name"
    else:
        return "There is no such name"

def remaining_days(days=7):
    upcoming_birthdays = []
    result = ""
    for record in phonebook.data.values():
        name = record.get_name()
        birthday = record.get_birthday()

        if birthday is not None:
            days_left = record.days_to_birthday()
            if days_left is not None and days_left <= int(days):
                upcoming_birthdays.append((name, birthday.value, days_left))

    if len(upcoming_birthdays) == 0:
        result = "No upcoming birthdays in the next few days."
    else:
        for name, birthday, days_left in upcoming_birthdays:
            result += f"{name}: birthday: {birthday} days to birthday: {days_left}\n"

    return result.rstrip()

@input_error
def get_phone_number(name):
    record = phonebook.get_records(name)
    if record:
        if record.phones:
            phones = [f"{record.get_name()}: {phone}" for phone in record.phones]
            result = "\n".join(phones)
            return result
        else:
            return "No phone number found for that name"
    else:
        return "There is no such name"


@input_error
def get_email(name):
    record = phonebook.get_records(name)
    if record:
        if record.emails:
            emails = [f"{record.get_name()}: {email}" for email in record.emails]
            result = "\n".join(emails)
            return result

        else:
            return "No email found for that name"

    else:
        return "There is no such name"


@input_error
def search_by_criteria(criteria: str, flag=None):
    if criteria:
        result = []
        result_str = ""
        for user in phonebook.data:
            record_str = phonebook.show_record(user)
            if flag is not None:
                criteria = criteria.lower()
                record_str = record_str.lower()
            if record_str.find(criteria) >= 0:
                result.append(phonebook.show_record(user))
        for el in result:
            result_str += el + "\n"
        if result == []:
            return f"No records found for that criteria"
        return result_str.rstrip()


@input_error
def iteration_note(page=1, count_hashtag=1):
    if not notebook.data:
        return "The notebook is empty"

    page = int(page)
    count_hashtag = int(count_hashtag)
    start_index = (page - 1) * count_hashtag
    end_index = start_index + count_hashtag

    records = list(notebook)
    total_pages = (len(records) + count_hashtag - 1) // count_hashtag

    if page < 1 or page > total_pages:
        return f"Invalid page number. Please enter a page number between 1 and {total_pages}"

    result = ""
    for record in records[start_index:end_index]:
        result += f"{record.hashtag}:\n"
        if record.notes:
            notes = "\n".join(
                [f"{note.value}\n---------------------" for note in record.notes]
            )
            result += f"\n{notes}\n"

    result += f"Page {page}/{total_pages}"

    return result.rstrip()


@input_error
def iteration(page=1, page_size=3):
    if not phonebook.data:
        return "The phonebook is empty"

    page = int(page)
    page_size = int(page_size)
    start_index = (page - 1) * page_size
    end_index = start_index + page_size

    records = list(phonebook)
    total_pages = (len(records) + page_size - 1) // page_size

    if page < 1 or page > total_pages:
        return f"Invalid page number. Please enter a page number between 1 and {total_pages}"

    result = ""
    for record in records[start_index:end_index]:
        result += f"{record}\n"

    result += f"Page {page}/{total_pages}"

    return result.rstrip()


def sorting_directory(folder):
    return sort_dir(Path(folder).resolve())


commands = {
    "hello": greeting,
    "help": help,
    "add": add_user,
    "note": add_note,
    "change": change_phone,
    "show all": show_all,
    "show notes": show_notes,
    "phone": get_phone_number,
    "exit": exit,
    "good bye": exit,
    "close": exit,
    "email": get_email,
    "birthday": get_birthday,
    "birthdays": remaining_days,
    "search": search_by_criteria,
    "page": iteration,
    "notes": iteration_note,
    "modify": change_note,
    "find": find_user_adressbook,
    "delete": del_record,
    "hashtag": get_note,
    "sort": sorting_directory,
}

filename1 = "address_book.bin"
filename2 = "note_book.bin"
phonebook = AddressBook()
notebook = Notebook()
console_view = ConsoleView()


def command_parser(user_input):
    command, *args = user_input.strip().split(" ")
    if not command.strip():
        return unknown_command, args
    try:
        handler = commands[command.lower()]

    except KeyError:
        if args:
            command_part2, *args = args[0].strip().split(" ", 1)
            command = command + " " + command_part2
        handler = commands.get(command.lower())
        if handler is None:
            user_input = change_command(user_input)
            if user_input is None:
                return unknown_command, args
            return command_parser(user_input)
    if command.lower() == "modify":
        args = [args[0], args[1], " ".join(args[2:])]
    elif command.lower() == "note":
        try:
            args = [" ".join(args)]
        except IndexError:
            pass
    return handler, args


def main():
    phonebook.load_address_book(filename1)
    notebook.load_notes(filename2)
    phonebook.display_contacts(console_view)
    notebook.display_notes(console_view)

    while True:
        user_input = input(">>> ")

        global cashe
        cashe = user_input

        handler, args = command_parser(user_input)
        result = handler(*args)

        if not result:
            print("Goodbye!")
            phonebook.save_address_book(filename1)
            notebook.save_notes(filename2)
            break
        print(result)


if __name__ == "__main__":
    main()
