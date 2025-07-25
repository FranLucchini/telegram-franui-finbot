import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder
from telegram.ext import CommandHandler
from database import Database

# Read .env file
load_dotenv()
logging.basicConfig(level=logging.INFO)
DB_NAME = os.environ.get('DB_NAME')
print(DB_NAME, flush=True)

def start():
    db_dir = os.path.dirname(DB_NAME)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    # Build database and tables
    db = Database(DB_NAME)
    db.create_table()
    db.close()


async def help_command(update, context):
    """Display help information about available commands"""
    help_text = """
🤖 **Expense Tracker Bot Help**

**Available Commands:**

💰 `/add <category> <amount> <description>`
   Add a new expense
   Example: `/add food 15.50 lunch at restaurant`

📊 `/get`
   Get all your expenses

📅 `/get_month_year <month> <year>`
   Get expenses for a specific month and year
   Example: `/get_month_year 12 2024`

❓ `/help`
   Show this help message

**Usage Tips:**
• Category: food, transport, entertainment, etc.
• Amount: Use numbers (decimals allowed)
• Description: Any text describing the expense

**Examples:**
• `/add transport 5.50 bus ticket`
• `/add groceries 45.20 weekly shopping`
• `/add entertainment 12.00 movie ticket`
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def start_command(update, context):
    """Welcome message when user starts the bot"""
    welcome_text = """
👋 **Welcome to the Expense Tracker Bot!**

I'll help you track your daily expenses easily.

Use `/help` to see all available commands or start adding expenses right away with:
`/add <category> <amount> <description>`

Example: `/add food 10.50 coffee and sandwich`
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')


async def add_expense(update, context):
    # Handle adding a new expense
    try:
        if len(context.args) < 3:
            await update.message.reply_text(
                "❌ Please provide category, amount, and description.\n"
                "Usage: `/add <category> <amount> <description>`\n"
                "Example: `/add food 15.50 lunch at restaurant`",
                parse_mode='Markdown'
            )
            return

        db = Database(DB_NAME)
        db.create_table()
        
        # Get the expense data from the user's message
        print(context.args)
        category = context.args[0]
        
        try:
            amount = float(context.args[1])
        except ValueError:
            await update.message.reply_text("❌ Amount must be a valid number!")
            return
            
        description = ' '.join(context.args[2:])
        
        db.insert_expense(category, amount, description)
        db.close()
        
        await update.message.reply_text(
            f'✅ **Expense Added!**\n'
            f'Category: {category}\n'
            f'Amount: ${amount:.2f}\n'
            f'Description: {description}',
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(f'❌ Error adding expense: {e}')


def print_expenses(expenses, month=None, year=None):
    if month and year:
        reply = f"📊 **Expenses for {month}/{year}:**\n\n"
    else:
        reply = '📊 **All Expenses:**\n\n'
    
    for expense in expenses:
        print(expense)
        # Format the expense datestring to be user friendly
        print(expense[1], type(expense[1]))
        date = f'{
            datetime.strptime(
                expense[1],
                "%Y-%m-%d %H:%M:%S.%f%z"
            ).strftime("%d/%m/%Y")
        }'
        reply += f'📅 {date} | 🏷️ {expense[2]} | 💰 ${expense[3]:.2f}\n📝 {expense[4]}\n\n'
    
    total = sum([expense[3] for expense in expenses])
    reply += f'💵 **Total: ${total:.2f}**'
    return reply


async def get_expenses(update, context):
    db = Database(DB_NAME)
    print("Getting all expenses...", flush=True)
    try:
        expenses = db.get_expenses()
        db.close()
        if expenses:
            reply = print_expenses(expenses)
            await update.message.reply_text(reply, parse_mode='Markdown')
        else:
            await update.message.reply_text('📭 No expenses found!')
    except Exception as e:
        await update.message.reply_text(f'❌ Error: {e}')


async def get_expenses_by_month(update, context):
    try:
        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ Please provide month and year.\n"
                "Usage: `/get_month_year <month> <year>`\n"
                "Example: `/get_month_year 12 2024`",
                parse_mode='Markdown'
            )
            return

        db = Database(DB_NAME)
        month = context.args[0]
        year = context.args[1]
        print(month, year, flush=True)
        
        expenses = db.get_expenses_by_month(month, year)
        db.close()
        
        if expenses:
            reply = print_expenses(expenses, month, year)
            await update.message.reply_text(reply, parse_mode='Markdown')
        else:
            await update.message.reply_text(f'📭 No expenses found for {month}/{year}!')
    except Exception as e:
        await update.message.reply_text(f'❌ Error: {e}')


def main():
    load_dotenv()
    # Read bot api token from .env file
    TOKEN = os.environ.get('TOKEN')
    # Print a message that the app is running
    print('Bot is running...', flush=True)
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('add', add_expense))
    app.add_handler(CommandHandler('get', get_expenses))
    app.add_handler(CommandHandler('get_month_year', get_expenses_by_month))
    
    start()
    app.run_polling()


if __name__ == '__main__':
    main()
