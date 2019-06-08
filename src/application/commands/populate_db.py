import os
import sys
import itertools
import logging

from config import Config
from application.models import QuizQuestion
from application.parser import QuizQuestionsFileParser

logger = logging.getLogger(__name__)


def run_command():
    """
    Populate redis database with provided quiz questions.
    """
    logger.debug(
        'Attempt to read files from directory {}.'.format(
            Config.QUIZ_QUESTIONS_DIRECTORY
        )
    )
    try:
        data_directory = Config.QUIZ_QUESTIONS_DIRECTORY
        files_list = [
            os.path.join(data_directory, filepath)
            for filepath in os.listdir(data_directory)
        ]
    except FileNotFoundError as e:
        logger.error(
            'An error has occurred during reading exploring directory.'
            'Directory: {}, error: {}'.format(Config.QUIZ_QUESTIONS_DIRECTORY, str(e))
        )
        sys.exit(1)

    logger.debug('DB population started.')
    logger.debug(files_list)
    populate_db_from_files(files_list)


def populate_db_from_files(quiz_questions_filepaths):
    quiz_questions_lists_generator = parse_quiz_questions_files(
        quiz_questions_filepaths, Config.DEFAULT_ENCODING
    )

    for quiz_questions_list in itertools.islice(
        quiz_questions_lists_generator, Config.QUIZ_QUESTIONS_FILEPARSING_LIMIT
    ):
        QuizQuestion.bulk_save_to_db(quiz_questions_list)


def parse_quiz_questions_files(quiz_questions_filepaths, encoding):
    for filepath in quiz_questions_filepaths:
        try:
            yield parse_quiz_question_file(filepath, encoding)
        except (IOError, FileNotFoundError) as e:
            logger.error(
                'An error has occurred during parsing file.'
                'File: {}, error: {}'.format(filepath, str(e))
            )
            continue


def parse_quiz_question_file(quiz_question_filepath, encoding):
    with open(quiz_question_filepath, 'r', encoding=encoding) as f:
        file_parser = QuizQuestionsFileParser(f)
        file_parser.parse_file()
        return file_parser.list_of_parsed_questions
