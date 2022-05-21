from telegram import InlineKeyboardButton

from dataclasses import dataclass


@dataclass
class Expense:
    id: int
    category: str
    amount: int
    date: str

    def __str__(self):
        return f'{self.amount} р. — {self.category} — {self.date}'


@dataclass
class Group:
    name: str
    sum: int

    def __str__(self):
        return f'{self.sum} р. — {self.name}'


@dataclass
class Category:
    name: str


class EntryList():
    entry_class = list

    def __init__(self, entries):
        self.entries = [self.entry_class(*elem) for elem in entries if elem[1]]

    def to_text(self):
        if not self.entries:
            return '— расходов нет. —'
        return '\n'.join(str(entry) for entry in self.entries)


class ExpenseList(EntryList):
    entry_class = Expense

    def to_keys(self):
        keys = [
            [InlineKeyboardButton(f'{expense}', callback_data=expense.id)]
            for expense in self.entries]
        keys.append([InlineKeyboardButton('ОТМЕНА', callback_data='ОТМЕНА')])
        return keys


class GroupList(EntryList):
    EntryClass = Group


class CategoryList(EntryList):
    BUTTON_COLS = 3

    def to_keys(self):
        list_range = range(0, len(self.entries), self.BUTTON_COLS)
        keys = [self.entries[i: i + self.BUTTON_COLS] for i in list_range]
        keys.append(['ОТМЕНА'])
        return keys
