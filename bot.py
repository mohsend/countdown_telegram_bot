import telegram, logging, random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

texts = {
    "new_game": """
Let's countdown! Who's down to play?
""",
    "imin": """Count me in! ({})""",
    "start_game": "Start the game",
    "help": """help text""",
    "pick_letters": """{}, it's your turn to pick the letters:
    `{}`""",
    "you_in": """You are in!""",
    "consonant": "Consonant",
    "vowel": "Vowel",
    "letters": "_________",
    "countdown": "Let's Countdown!"
}

def letters_keyboard():
    keyboard = [ [ InlineKeyboardButton(texts["consonant"], callback_data='c'),
                 InlineKeyboardButton(texts["vowel"], callback_data='v') ] ]
    return InlineKeyboardMarkup(keyboard)

def countdown_keyboard():
    keyboard = [ [ InlineKeyboardButton(texts["countdown"], callback_data='countdown') ] ]
    return InlineKeyboardMarkup(keyboard)

keyboards = {
    "letters": letters_keyboard(),
    "countdown": countdown_keyboard()
}


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text(texts["help"])

def new_game(bot, update):
    """Send a message when the command /help is issued."""
    keyboard = [ [ InlineKeyboardButton(texts["imin"].format(0), callback_data='in'),
                    InlineKeyboardButton(texts["start_game"], callback_data='start') ] ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id=update.message.chat_id, text=texts["new_game"],
                    reply_markup=reply_markup)

def pick_letters(bot, update, user_data):
    query = update.callback_query
    user_data['letters'] = texts['letters']
    user_data['howmany'] = 0
    bot.send_message(chat_id=query.message.chat_id, text=texts["pick_letters"].format(query.message.from_user.first_name, user_data['letters']),
                    reply_markup=keyboards["letters"], parse_mode=telegram.ParseMode.MARKDOWN)

def button(bot, update, user_data):
    query = update.callback_query
    data  = query.data
    if data == 'c' or data == 'v':
        # append a letter
        user_data['letters'] = user_data['letters'].replace('_', get_letter(data), 1)
        user_data['howmany'] += 1
        
        # select keyboard markup
        reply_m = keyboards["letters"]
        if user_data['howmany'] == 9:
            reply_m = keyboards["countdown"]
        
        bot.edit_message_text(text=texts["pick_letters"].format(query.message.from_user.first_name, user_data['letters']),
                          reply_markup=reply_m,
                          parse_mode=telegram.ParseMode.MARKDOWN,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
    elif data == 'in':
        bot.send_message(chat_id=update.callback_query.id, text=texts["you_in"])
    elif data == 'start':
        pick_letters(bot, update, user_data)

def get_letter(t):
    consonant = [ 'B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'X', 'Z', 'W', 'Y' ]
    vowel = [ 'A', 'E', 'I', 'O', 'U' ]
    if t == 'c':
        return consonant[random.randrange(0, 20)]
    else:
        return vowel[random.randrange(0, 4)]

def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    token_file = open("token.txt","r")
    token = token_file.read().rstrip()
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", help))
    dp.add_handler(CommandHandler("newGame", new_game))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram

    # on inline buttom press
    dp.add_handler(CallbackQueryHandler(button, pass_user_data=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
