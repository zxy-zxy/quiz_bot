import os
import sys
import itertools
import logging

from redis import exceptions as redis_exceptions

from application.models import QuizQuestion
from application.parser import QuizQuestionsFileParser

logger = logging.getLogger(__name__)


def run_command(quiz_questions_directory, default_encoding, files_limit=None):
    """
    Populate redis database with quiz questions from provided files.
    """
    logger.debug(
        'Attempt to read files from directory {}.'.format(quiz_questions_directory)
    )
    try:
        data_directory = quiz_questions_directory
        files_list = [
            os.path.join(data_directory, filepath)
            for filepath in os.listdir(data_directory)
        ]
    except FileNotFoundError as e:
        logger.error(
            'An error has occurred during reading exploring directory.'
            'Directory: {}, error: {}'.format(quiz_questions_directory, str(e))
        )
        sys.exit(1)

    logger.debug('DB population started.')
    logger.debug(files_list)
    populate_db_from_files(files_list, default_encoding, files_limit)


def populate_db_from_files(quiz_questions_filepaths, default_encoding, files_limit):
    """
    :param quiz_questions_filepaths: list of filepaths to files with questions
    :param default_encoding: target files encoding
    :param files_limit if we want to limit how many files we want to parse:
    Main function of this module, save questions into database.
    """
    quiz_questions_lists_generator = parse_quiz_questions_files(
        quiz_questions_filepaths, default_encoding
    )

    for quiz_questions_list in itertools.islice(
            quiz_questions_lists_generator, files_limit
    ):
        try:
            QuizQuestion.bulk_save_to_db(quiz_questions_list)
        except redis_exceptions.RedisError as e:
            logger.error(str(e))


def parse_quiz_questions_files(quiz_questions_filepaths, encoding):
    """
    yields list of QuizQuestion objects.
    """
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
    """
    :param quiz_question_filepath: filepath to concrete file with questions
    :param encoding: default encoding of concrete file
    :return: list of QuizQuestion objects.
    """
    with open(quiz_question_filepath, 'r', encoding=encoding) as f:
        quiz_question_file_parser = QuizQuestionsFileParser(f)

        question_list = [
            question
            for question in convert_question_dict_to_object(quiz_question_file_parser)
        ]
        return question_list


def convert_question_dict_to_object(quiz_question_file_parser):
    """
    Iterate over content of the file,
    convert dict into QuizQuestion object, yield it.
    """
    for question_dict in quiz_question_file_parser:
        try:
            quiz_question = QuizQuestion(**question_dict)
            logger.debug(
                'Question {} from file {} converted into model object successfully.'.format(
                    quiz_question, quiz_question_file_parser.open_file.name
                )
            )
            yield quiz_question
        except ValueError as e:
            logger.error(
                'An error {} has occurred during parsing file: {}'.format(
                    str(e), quiz_question_file_parser.open_file.name
                )
            )
