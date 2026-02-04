
"""A terminal-based assistant bot that allows users to add, change and view contacts"""
from address_book import AddressBook, Record, save_data_to_file, load_data_from_file


def input_error(func):
    """Decorator that handles user input errors for command handlers."""

    def inner(*args, **kwargs):
        """Inner function that handles errors and returns appropriate messages."""
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e) or "Give me name and phone please."
        except IndexError:
            return "Enter the argument for the command"
        except KeyError:
            return "Contact not found"
        except AttributeError:
            return "Contact not found"
    return inner


def parse_input(user_input: str) -> tuple[str, list[str]]:
    """Function that prepares user input for the next steps"""
    parts = user_input.strip().split()
    if not parts:
        return "", []
    command = parts[0].lower()
    args = parts[1:]
    return command, args

@input_error
def add_contact(args: list[str], book: AddressBook) -> str:
    """Function that allows creating and saving a contact with name and phone number"""
    name, phone = args

    record = book.find(name)
    if record is None:
        record = Record(name)
        book.add_record(record)

    record.add_phone(phone)
    return "Contact added"

@input_error
def change_contact(args: list[str], book: AddressBook) -> str:
    """Function that allows changing the phone number of an existing contact"""
    name, old_phone, new_phone = args

    record = book.find(name)
    record.edit_phone(old_phone, new_phone)

    return "Contact updated"

@input_error
def show_phone(args: list[str], book: AddressBook) -> str:
    """Shows contact details for a specific name"""
    name = args[0]

    record = book.find(name)

    if not record.phones:
        return "No phones saved for this contact"
    return "; ".join(p.value for p in record.phones)



@input_error
def show_all(args: list[str], book: AddressBook) -> str:
    """Function that allows showing all saved contacts"""
    return str(book)


@input_error
def add_birthday(args: list[str], book: AddressBook) -> str:
    """Function that allows adding a birthday to an existing contact"""
    name, birthday = args

    record = book.find(name)

    record.add_birthday(birthday)
    return "Birthday added"


@input_error
def show_birthday(args: list[str], book: AddressBook) -> str:
    """Shows the birthday of a specific contact"""
    name = args[0]

    record = book.find(name)

    if record.birthday is None:
        return "No birthday saved for this contact"
    return str(record.birthday)

@input_error
def birthdays(args: list[str], book: AddressBook) -> str:
    """Shows upcoming birthdays in the next 7 days"""
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."

    lines = []
    for item in upcoming:
        lines.append(f"{item['name']}: {item['birthday']}")
    return "\n".join(lines)

def main() -> None:
    """Starts the assistant bot and manages the command processing loop"""
    book = load_data_from_file("addressbook.pkl")

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ("close", "exit"):
            print("Good bye!")
            save_data_to_file(book)
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
            print(show_all(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        elif command == "":
            continue
        else:
            print("Invalid command")

if __name__ == "__main__":
    main()
