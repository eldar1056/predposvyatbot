from telegram.ext import Application, CommandHandler, MessageHandler, filters
from code.commands import *
from code.response import handle_messages


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Error: {update} caused error {context.error}')
    log_response(update, "logs/error_log.txt", str(update) + ': ' + str(context.error))


def main():
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    data = Data(ERASE_DATA)

    if RESET_COUNT:
        reset_count()

    print()
    print(data.get_roles())
    print()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('status', status_command))
    app.add_handler(CommandHandler('stages', stages_command))
    app.add_handler(CommandHandler('scores', scores_command))
    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_messages))

    # Errors
    app.add_error_handler(error)

    # Polling
    print("Polling...")
    app.run_polling(poll_interval=1)


main()
