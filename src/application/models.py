import logging
import reprlib

from application.common.database import RedisStorage

logger = logging.getLogger(__name__)


class QuizQuestion:
    COLLECTION = 'quiz-questions'

    def __init__(self, question, answer, comment, source, author):
        self.question = question
        self.answer = answer
        self.comment = comment
        self.source = source
        self.author = author

        if not self.question:
            error_message = 'Question text is not presented.'
            logger.error(error_message)
            raise ValueError(error_message)
        if not self.answer:
            error_message = 'Answer text is not presented.'
            logger.error(error_message)
            raise ValueError(error_message)

    def __str__(self):
        preview = f'Question: {self.question}. Answer: {self.answer}.'
        return reprlib.repr(preview)

    def __repr__(self):
        preview = f'Question: {self.question}. Answer: {self.answer}.'
        return reprlib.repr(preview)

    def to_dict(self):
        return {
            'question': self.question,
            'answer': self.answer,
            'comment': self.comment,
            'source': self.source,
            'author': self.author,
        }

    def save_to_db(self):
        return RedisStorage.add_records_to_set(QuizQuestion.COLLECTION, self)

    @staticmethod
    def bulk_save_to_db(quiz_questions_list):
        return RedisStorage.add_records_to_set(
            QuizQuestion.COLLECTION, quiz_questions_list
        )

    @classmethod
    def get_random_question_from_storage(cls):
        random_question_dict = RedisStorage.get_random_record_from_set(
            QuizQuestion.COLLECTION
        )
        quiz_question = cls(**random_question_dict)
        return quiz_question


class UserQuestion:
    TABLE_PREFIX = 'users_questions'

    def __init__(self, user_id, question):
        self.user_id = user_id
        self.question = question

    def save_to_db(self):
        key = f'{UserQuestion.TABLE_PREFIX}_{self.user_id}'
        return RedisStorage.set(key, self.question)

    @classmethod
    def get_by_user_id(cls, user_id):
        key = f'{UserQuestion.TABLE_PREFIX}_{user_id}'
        question_text = RedisStorage.get(key)
        return cls(user_id, question_text)


class UserRating:
    TABLE_PREFIX = 'users_ratings'

    def __init__(self, user_id):
        self.user_id = user_id

    def get_rating(self):
        rating = RedisStorage.get(f'{UserRating.TABLE_PREFIX}_{self.user_id}')
        return 0 if rating is None else rating

    def set_rating(self, value):
        return RedisStorage.set(f'{UserRating.TABLE_PREFIX}_{self.user_id}', value)

    def increase_rating(self, increment=1):
        return RedisStorage.increase_value(
            f'{UserRating.TABLE_PREFIX}_{self.user_id}', increment
        )
