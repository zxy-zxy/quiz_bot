import logging
import json
import dataclasses

from telegram.ext import (
    Updater,
    MessageHandler,
    Filters,
    ConversationHandler,
    CommandHandler,
    RegexHandler,
)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from redis import exceptions as redis_exceptions

from application.models import QuizQuestion, UserQuestion, UserRating

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, token):
        self.updater = Updater(token=token)

        dispatcher = self.updater.dispatcher
        dispatcher.add_error_handler(self._error)
        self._initialize_conversation_handler()

    def start(self):
        self.updater.start_polling()
        self.updater.idle()

    def _error(self, bot, update, error):
        logger.error(f'Update {str(update)} caused error {str(error)}.')

    def _initialize_conversation_handler(self):
        dispatcher = self.updater.dispatcher

        conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('start', ConversationStates.start)],
            states={
                ConversationStates.MENU_CHOOSING: [
                    RegexHandler(
                        '^(Новый вопрос)$',
                        ConversationStates.new_question_chosen_state,
                        pass_user_data=True,
                    ),
                    RegexHandler(
                        '^(Мой счет)$',
                        ConversationStates.user_score_state,
                        pass_user_data=True,
                    ),
                ],
                ConversationStates.USER_ANSWER_PROCESSING: [
                    RegexHandler(
                        '^(Сдаться)$',
                        ConversationStates.give_up_state,
                        pass_user_data=True,
                    ),
                    MessageHandler(
                        Filters.text,
                        ConversationStates.user_answered_state,
                        pass_user_data=True,
                    ),
                ],
            },
            fallbacks=[CommandHandler('cancel', ConversationStates.cancel)],
        )
        dispatcher.add_handler(conversation_handler)


class ConversationStates:
    MENU_CHOOSING, USER_ANSWER_PROCESSING = range(2)
    keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]

    @staticmethod
    def start(bot, update):
        keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
        message = 'Привет! Я бот для викторин!'
        reply_markup = ReplyKeyboardMarkup(
            keyboard, one_time_keyboard=True, resize_keyboard=True
        )
        update.message.reply_text(message, reply_markup=reply_markup)
        return ConversationStates.MENU_CHOOSING

    @staticmethod
    def cancel(bot, update):
        user = update.message.from_user
        user_first_name = user['first_name']
        update.message.reply_text(
            f'До свидания {user_first_name}!.', reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    @staticmethod
    def new_question_chosen_state(bot, update, user_data):

        try:
            quiz_question = QuizQuestion.get_random_question_from_storage()
        except (redis_exceptions.DataError, ValueError) as e:
            logger.error(
                'An error occurred during object initialization. '
                'User_id: {}, error: {}'.format(update.message.chat_id, str(e))
            )
            update.message.reply_text('Пожалуйста, попробуйте снова.')
            return ConversationStates.MENU_CHOOSING

        try:
            user_question = UserQuestion(
                update.message.chat_id, json.dumps(dataclasses.asdict(quiz_question))
            )
            user_question.save_to_db()
        except redis_exceptions.DataError as e:
            logger.error(
                'An error occurred during saving data to database.'
                'User_id: {}, record: {}, error: {}'.format(
                    update.message.chat_id, dataclasses.asdict(quiz_question), str(e)
                )
            )
            update.message.reply_text('Пожалуйста, попробуйте снова.')
            return ConversationStates.MENU_CHOOSING

        update.message.reply_text(quiz_question.question)
        return ConversationStates.USER_ANSWER_PROCESSING

    @staticmethod
    def user_answered_state(bot, update, user_data):
        user_question = UserQuestion.get_by_user_id(update.message.chat_id)

        if user_question.question is None:
            update.message.reply_text('Пожалуйста, попробуйте снова.')
            return ConversationStates.MENU_CHOOSING

        quiz_question_dict = json.loads(user_question.question)
        quiz_question = QuizQuestion(**quiz_question_dict)

        normalized_answer_from_user = update.message.text.lower().strip()
        normalized_answer_from_base = quiz_question.answer.lower().strip()

        if normalized_answer_from_base == normalized_answer_from_user:
            user_rating = UserRating(update.message.chat_id)
            user_rating.increase_rating()

            update.message.reply_text(
                'Правильно! Поздравляю! Для следующего вопроса нажмите «Новый вопрос».'
            )

            return ConversationStates.MENU_CHOOSING

        update.message.reply_text('Неправильно... Попробуешь ещё раз?')
        return ConversationStates.USER_ANSWER_PROCESSING

    @staticmethod
    def give_up_state(bot, update, user_data):
        user_question = UserQuestion.get_by_user_id(update.message.chat_id)

        if user_question.question is None:
            update.message.reply_text('Пожалуйста, попробуйте снова.')
            return ConversationStates.MENU_CHOOSING

        quiz_question_dict = json.loads(user_question.question)
        quiz_question = QuizQuestion(**quiz_question_dict)

        update.message.reply_text(
            f'Внимание, правильный ответ: {quiz_question.answer}'
            f'Для следующего вопроса нажмите «Новый вопрос».'
        )
        return ConversationStates.MENU_CHOOSING

    @staticmethod
    def user_score_state(bot, update, user_data):
        user_rating = UserRating(update.message.chat_id)
        score = user_rating.get_rating()
        update.message.reply_text(f'Ваш  результат: {score}')
        return ConversationStates.MENU_CHOOSING
