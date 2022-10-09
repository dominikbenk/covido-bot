#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import sys
from collections import namedtuple
import unidecode

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

sys.path.append('../dialmonkey-npfl123')

from dialmonkey.utils import load_conf, run_for_n_iterations, DialMonkeyFormatter
from dialmonkey.conversation_handler import ConversationHandler
from dialmonkey.dialogue import Dialogue
import json


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

ARGS = namedtuple('ARGS', ['conf', 'logging_level', 'user_stream_type', 'input_file', 'output_stream_type', 'output_file', 'num_dials'])
ARGS.__new__.__defaults__ = (None,) * len(ARGS._fields)

args = ARGS(conf='./conf/text_covid.yaml', num_dials=1, logging_level='ERROR')

# loading the configuration file
conf = load_conf(args.conf)

handler = ConversationHandler(conf, logger, should_continue=run_for_n_iterations(args.num_dials))

dial = Dialogue()
handler._reset_components()
handler._init_components(dial)

# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Vítejte v databázi monitorujících vývoj onemocnění COVID-19 v České republice, jak Vám mohu poradit?')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def reply_telegram(update: Update, context: CallbackContext) -> None:
    global dial
    print("USER INPUT: " + update.message.text)
    input_adjusted = unidecode.unidecode(update.message.text.lower())
    response = handler.get_response(dial, input_adjusted)[0] 
    update.message.reply_text(response)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    token = json.load(open('tokens.json'))['telegram-api-token']
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, reply_telegram))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()