import random
import logging
import json
import dataclasses

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from redis import exceptions as redis_exceptions

from application.models import QuizQuestion, UserQuestion, UserRating

logger = logging.getLogger(__name__)


class VkBot:
    GREETINGS, MENU_CHOOSING, USER_ANSWER_PROCESSING = range(3)

    def __init__(self, group_token):
        self._vk_session = vk_api.VkApi(token=group_token)
        self._vk_api = self._vk_session.get_api()
        self._longpoll = VkLongPoll(self._vk_session)
        self._state = VkBot.GREETINGS

    def start(self):
        for event in self._longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if self._state == VkBot.GREETINGS:
                    self._greetings_state(event)
                elif self._state == VkBot.MENU_CHOOSING:
                    self._menu_choosing_state(event)
                elif self._state == VkBot.USER_ANSWER_PROCESSING:
                    self._answer_processing_state(event)

    def _greetings_state(self, event):

        keyboard = VkKeyboard()
        keyboard.add_button('Новый вопрос', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('Сдаться', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Мой счет', color=VkKeyboardColor.DEFAULT)

        self._vk_api.messages.send(
            user_id=event.user_id,
            message='Привет! Я бот для викторин!',
            keyboard=keyboard.get_keyboard(),
            random_id=random.randint(1, 1000),
        )
        self._state = VkBot.MENU_CHOOSING

    def _menu_choosing_state(self, event):
        if event.text == 'Новый вопрос':

            try:
                quiz_question = QuizQuestion.get_random_question_from_storage()
            except (redis_exceptions.DataError, ValueError) as e:
                logger.error(
                    'An error occurred during object initialization. '
                    'User_id: {}, error: {}'.format(
                        event.user_id.message.chat_id, str(e)
                    )
                )
                self._vk_api.messages.send(
                    user_id=event.user_id,
                    message='Пожалуйста, попробуйте снова.',
                    random_id=random.randint(1, 1000),
                )
                self._state = VkBot.MENU_CHOOSING
                return None

            try:
                user_question = UserQuestion(
                    event.user_id, json.dumps(dataclasses.asdict(quiz_question))
                )
                user_question.save_to_db()
            except redis_exceptions.DataError as e:
                logger.error(
                    'An error occurred during saving data to database.'
                    'User_id: {}, record: {}, error: {}'.format(
                        event.user_id.message.chat_id,
                        dataclasses.asdict(quiz_question),
                        str(e),
                    )
                )
                self._vk_api.messages.send(
                    user_id=event.user_id,
                    message='Пожалуйста, попробуйте снова.',
                    random_id=random.randint(1, 1000),
                )
                self._state = VkBot.MENU_CHOOSING
                return None

            self._vk_api.messages.send(
                user_id=event.user_id,
                message=quiz_question.question,
                random_id=random.randint(1, 1000),
            )
            self._state = VkBot.USER_ANSWER_PROCESSING

        elif event.text == 'Мой счет':

            user_rating = UserRating(event.user_id)
            score = user_rating.get_rating()

            self._vk_api.messages.send(
                user_id=event.user_id,
                message=f'Ваш  результат: {score}',
                random_id=random.randint(1, 1000),
            )

            self._state = VkBot.MENU_CHOOSING
            return None

    def _answer_processing_state(self, event):

        user_question = UserQuestion.get_by_user_id(event.user_id)

        if event.text == 'Сдаться':

            if user_question.question is None:
                self._vk_api.messages.send(
                    user_id=event.user_id,
                    message='Пожалуйста, попробуйте снова.',
                    random_id=random.randint(1, 1000),
                )
                self._state = VkBot.MENU_CHOOSING
                return None

            quiz_question_dict = json.loads(user_question.question)
            quiz_question = QuizQuestion(**quiz_question_dict)

            self._vk_api.messages.send(
                user_id=event.user_id,
                message=f'Внимание, правильный ответ: {quiz_question.answer}'
                f'Для следующего вопроса нажмите «Новый вопрос».',
                random_id=random.randint(1, 1000),
            )

            self._state = VkBot.MENU_CHOOSING
            return None

        if user_question.question is None:
            self._vk_api.messages.send(
                user_id=event.user_id,
                message='Пожалуйста, попробуйте снова.',
                random_id=random.randint(1, 1000),
            )
            self._state = VkBot.MENU_CHOOSING
            return None

        quiz_question_dict = json.loads(user_question.question)
        quiz_question = QuizQuestion(**quiz_question_dict)

        normalized_answer_from_user = event.text.lower().strip()
        normalized_answer_from_base = quiz_question.answer.lower().strip()

        if normalized_answer_from_base == normalized_answer_from_user:
            user_rating = UserRating(event.user_id)
            user_rating.increase_rating()

            self._vk_api.messages.send(
                user_id=event.user_id,
                message='Правильно! Поздравляю! '
                'Для следующего вопроса нажмите «Новый вопрос».',
                random_id=random.randint(1, 1000),
            )
            self._state = VkBot.MENU_CHOOSING
            return None

        self._vk_api.messages.send(
            user_id=event.user_id,
            message='Неправильно... Попробуешь ещё раз?',
            random_id=random.randint(1, 1000),
        )

        self._state = VkBot.USER_ANSWER_PROCESSING
        return None
