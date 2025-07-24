import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder
from telegram.ext import CommandHandler

from database import Database
# Read .env file

logging.basicConfig(level=logging.INFO)
DB_NAME = 'expenses.db'


async def start(update, context):
    # Build database and tables
    db = Database(DB_NAME)
    db.create_table()
    db.close()
    await update.message.reply_text('Welcome to the expense tracker bot!')


async def add_expense(update, context):
    # Handle adding a new expense
    db = Database(DB_NAME)
    db.create_table()

    # Get the expense data from the user's message
    print(context.args)
    category = context.args[0]
    amount = float(context.args[1])
    description = ' '.join(context.args[2:])

    db.insert_expense(category, amount, description)
    db.close()

    await update.message.reply_text('Expense added!')


def print_expenses(expenses, month=None, year=None):
    if month and year:
        reply = f"Expenses for {month}/{year}:\n"
    else:
        reply = 'Expenses:\n'
    for expense in expenses:
        print(expense)
        # Format the expense datestring to be user friendly
        print(expense[1], type(expense[1]))
        date = f'{
            datetime.strptime(
                expense[1],
                '%Y-%m-%d %H:%M:%S.%f%z'
            ).strftime("%d/%m/%Y")
        }'
        reply += f'\t ► {date} |{expense[2]}| ${expense[3]}| {expense[4]}|\n'
    reply += f'Total: {sum([expense[3] for expense in expenses])}'
    return reply


async def get_expenses(update, context):
    db = Database(DB_NAME)
    try:
        expenses = db.get_expenses()
        db.close()

        if expenses:
            reply = print_expenses(expenses)
            await update.message.reply_text(reply)
        else:
            await update.message.reply_text('No expenses found!')
    except Exception as e:
        await update.message.reply_text(f'Error: {e}')


async def get_expenses_by_month(update, context):
    db = Database(DB_NAME)
    month = context.args[0]
    year = context.args[1]
    print(month, year, flush=True)
    expenses = db.get_expenses_by_month(month, year)
    db.close()

    if expenses:
        reply = print_expenses(expenses, month, year)
        await update.message.reply_text(reply)
    else:
        await update.message.reply_text('No expenses found!')


def main():
    load_dotenv()
    # Read bot api token fron .env file
    TOKEN = os.environ.get('TOKEN')

    # Print a message that the app is running
    print('Bot is running...', flush=True)

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('add', add_expense))
    app.add_handler(CommandHandler('get', get_expenses))
    app.add_handler(CommandHandler('get_month_year', get_expenses_by_month))

    app.run_polling()


if __name__ == '__main__':
    main()
