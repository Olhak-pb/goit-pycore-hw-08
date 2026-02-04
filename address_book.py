
"""A terminal-based assistant bot that allows users to add, change and view contacts"""
from __future__ import annotations

from collections import UserDict

from datetime import datetime, date, timedelta

class Field:
    """Base class for fields of a contact."""
    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

class Name(Field):
    """Name must not be empty."""
    pass

class Phone(Field):
    """Phone must contain exact 10 digits."""

    def __init__(self, value: str):
        value = str(value)
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)

class Birthday(Field):
    """Birthday must be in DD.MM.YYYY format"""

    def __init__(self, value: str):
        value = str(value)
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Please use DD.MM.YYYY")
        super().__init__(value)

    def to_date(self) -> date:
        """Converting birthday to a date object."""
        return datetime.strptime(self.value, "%d.%m.%Y").date()



class Record:
    """A class that represents a contact."""
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.birthday: Birthday | None = None

    def find_phone(self, phone: str) -> Phone | None:
        """Finds a phone number in the list of phones."""
        for p in self.phones:
            if p.value == phone:
                return p
        return None
        
    def add_phone(self, phone: str) -> None:
        """Adds a new phone number to the list of phones."""
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str) -> None:
        """Removes a phone number from the list of phones."""
        found_phone = self.find_phone(phone)
        if found_phone:
            self.phones.remove(found_phone)

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        """Changes a phone number in the list of phones."""
        found_phone = self.find_phone(old_phone)
        if not found_phone:
            raise ValueError("Old phone number not found.")
        self.phones[self.phones.index(found_phone)] = Phone(new_phone)

    def add_birthday(self, birthday: str) -> None:
        """Adds a birthday to the contact."""
        self.birthday = Birthday(birthday)

    def __str__(self) -> str:
        phones_str = "; ".join(p.value for p in self.phones) if self.phones else "-"
        bday_str = str(self.birthday) if self.birthday else "-"
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {bday_str}"


class AddressBook(UserDict):
    """A dictionary-like class that stores contacts."""
    def add_record(self, record: Record) -> None:
        """Adds a new contact."""
        self.data[record.name.value] = record

    def find(self, name: str) -> Record | None:
        """Finds a contact by name."""
        return self.data.get(name)

    def delete(self, name: str) -> None:
        """Deletes a contact by name."""
        self.data.pop(name, None)

    def get_upcoming_birthdays(self) -> list[dict[str, str]]:
        """Returns a list of upcoming birthdays in the format {"name": ..., "birthday": ...}"""
        today = date.today()
        end_day = today + timedelta(days=7)

        result: list[dict[str, str]] = []

        for record in self.data.values():
            congrats = self._get_congrats_date(record, today)
            if congrats is None:
                continue

            if today <= congrats <= end_day:
                result.append({
                    "name": record.name.value,
                    "birthday": congrats.strftime("%d.%m.%Y"),
                })
        return result

    def _get_congrats_date(self, record, today: date):
        if record.birthday is None:
            return None

        bday = record.birthday.to_date()

        try:
            bday_this_year = bday.replace(year=today.year)
        except ValueError:
            return None

        if bday_this_year < today:
            try:
                bday_this_year = bday.replace(year=today.year + 1)
            except ValueError:
                return None

        return self._move_to_monday_if_weekend(bday_this_year)

    @staticmethod
    def _move_to_monday_if_weekend(d: date) -> date:
        wd = d.weekday()
        if wd == 5:
            return d + timedelta(days=2)
        if wd == 6:
            return d + timedelta(days=1)
        return d

    def __str__(self) -> str:
        if not self.data:
            return "No contacts saved."
        return "\n".join(str(record) for record in self.data.values())
