import pickle
import os
from collections import UserDict
import re
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    
class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError("Phone number must be 10 digits long.")
        super().__init__(value)

    @staticmethod
    def validate(value):
        return bool(re.match(r'^\d{10}$', value))
    
class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = self.validate_and_convert(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
    @staticmethod
    def validate_and_convert(value):
        return datetime.strptime(value, "%d.%m.%Y")
    
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)

    def remove_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                self.phones.remove(phone)
                return True
        return False
    
    def edit_phone(self, old_number, new_number):
        for i, phone in enumerate(self.phones):
            if phone.value == old_number:
                self.phones[i] = Phone(new_number)
                return True
        print(f"Old phone number {old_number} not found.")
        return False
    
    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone.value
        return None
    
    def change_phone(self, old_number: str, new_number: str):
        for phone in self.phones:
            if phone.value == old_number:
                phone.value = new_number
                return
        raise ValueError(f"Phone number '{old_number}' not found.")
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        birthday_str = f", birthday: {self.birthday.value.strftime('%d.%m.%Y')}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return True
        print(f"Contact {name} not found.")
        return False
    
    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.now()
        next_week = today + timedelta(days=7)

        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if today <= birthday_this_year <= next_week:
                    upcoming_birthdays.append(record)
        return upcoming_birthdays
    
    def show_all_contacts(self):
        if not self.data:
            return "No contacts found."
        return "\n".join(str(record) for record in self.data.values())

    def save_to_file(self, filename="address_book.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self.data, f)

    def load_from_file(self, filename="address_book.pkl"):
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                self.data = pickle.load(f)

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (IndexError, ValueError) as e:
            return str(e)
    return wrapper

@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        return "Please provide both name and phone number."
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    if len(args) < 3:
        return "Please provide a name, old phone number, and new phone number."
   # Змінюємо телефонний номер контакту.
    name, old_number, new_number = args
    record = book.find(name)
    if record is None:
        return f"Contact {name} does not exist."
    if old_number not in [phone.value for phone in record.phones]:
        return f"Old phone number '{old_number}' not found for contact '{name}'."
    if record.edit_phone(old_number, new_number):
        return f"Phone number changed from {old_number} to {new_number} for {name}."
    else:
        return f"Phone number {old_number} not found for {name}."

@input_error
def show_phone(args, book):
    # Показуємо телефонний номер контакту.
    name = args[0]
    record = book.find(name)
    if record is None or not record.phones:
        return f"No phone number found for {name}."
    
    return f"{name}'s phone number(s): {', '.join(phone.value for phone in record.phones)}"

@input_error
def show_all_contacts(book):
    # Показуємо всі контакти в адресній книзі.
    return book.show_all_contacts()

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record is None:
        return f"Contact {name} does not exist."
    record.add_birthday(birthday)
    return f"Birthday for {name} added."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record is None or record.birthday is None:
        return f"No birthday found for {name}."
    return f"{name}'s birthday is on {record.birthday.value.strftime('%d.%m.%Y')}."

@input_error
def birthdays(args, book):
    today = datetime.now()
    next_week = today + timedelta(days=7)
    upcoming_birthdays = []

    for record in book.data.values():
        if record.birthday:
            birthday_this_year = record.birthday.value.replace(year=today.year)
            if today <= birthday_this_year <= next_week:
                upcoming_birthdays.append(f"{record.name.value}: {birthday_this_year.strftime('%d.%m.%Y')}")
    if not upcoming_birthdays:
        return "No upcoming birthdays in the next week."
    return "Upcoming birthdays:\\n" + "\\n".join(upcoming_birthdays)

def parse_input(user_input):
    return user_input.strip().split()

def main():
    book = AddressBook()
    book.load_from_file()
    print("Welcome to the assistant bot!")

    try:
        while True:
            user_input = input("Enter a command (add/show/exit): ").strip().lower()
            command, *args = parse_input(user_input)

            if command in ["close", "exit"]:
                print("Good bye!")
                break
            elif command == "hello":
                print("How can I help you?")
            elif command == "add":
                print(add_contact(args, book))
            elif command == "change":
                print(change_contact(args, book))  
            elif command == "phone":
                print(show_phone(args, book))  
            elif command == "all":
                print(show_all_contacts(book))  
            elif command == "add-birthday":
                print(add_birthday(args, book))
            elif command == "show-birthday":
                print(show_birthday(args, book))
            elif command == "birthdays":
                print(birthdays(args, book))
            else:
                print("Invalid command.")

    finally:
        book.save_to_file()

if __name__ == "__main__":
    main()

    # Створення новоі адресноі книги
    book = AddressBook()

    # Створення запису для John
    john_record = Record("John")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")

    # Додавання запису John до адресної книги
    book.add_record(john_record)

    # Створення та додавання нового запису для Jane
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    book.add_record(jane_record)

    josh_record = Record("Josh")
    josh_record.add_phone("9876548810")
    book.add_record(josh_record)

    # Виведення всіх записів у книзі
    for name, record in book.data.items():
        print(record)

    # Знаходження та редагування телефону для John
    john = book.find("John")
    john.edit_phone("1234567890", "1112223333")
    print(john)  # Виведення: Contact name: John, phones: 1112223333; 5555555555

    # Пошук конкретного телефону у записі John
    found_phone = john.find_phone("5555555555")
    print(f"{john.name}: {found_phone}")  # Виведення: 5555555555

    # Видалення запису Jane
    book.delete("Jane")

    # Додавання контактів
    contact1 = Record("Alice")
    contact1.add_phone("1234567890")
    contact1.add_birthday("15.05.1990")
    
    contact2 = Record("Bob")
    contact2.add_phone("0987654321")
    contact2.add_birthday("12.08.1985")

    book.add_record(contact1)
    book.add_record(contact2)

    # Виведення контактів
    for record in book.data.values():
        print(record)

    # Отримання майбутніх днів народження
    upcoming_birthdays = book.get_upcoming_birthdays()
    print("\nUpcoming birthdays:")
    for record in upcoming_birthdays:
        print(record)