import re
import logging

from application.models import QuizQuestion

logger = logging.getLogger(__name__)


class QuizQuestionsFileParser:
    """
    Parses specific file format to an array of dictionaries with keys:
    - question
    - answer
    - comment
    - source
    - author
    """

    rx_dict = {
        'question': re.compile(r'(?P<question>Вопрос \d+:)\n'),
        'answer': re.compile(r'(?P<answer>Ответ:)\n'),
        'comment': re.compile(r'(?P<answer>Комментарий:)\n'),
        'source': re.compile(r'(?P<answer>Источник:)\n'),
        'author': re.compile(r'(?P<answer>Автор:)\n'),
    }

    def __init__(self, open_file):
        self.open_file = open_file
        self.list_of_parsed_questions = list()

    def parse_file(self):
        line = self.open_file.readline()
        current_question_dict = self.initialize_step_question_dict()

        while line:
            key = self._parse_line(line)
            if key is None:
                line = self.open_file.readline()
                continue

            if key == 'question':

                if current_question_dict['question']:

                    try:
                        quiz_question = QuizQuestion(**current_question_dict)
                        self.list_of_parsed_questions.append(quiz_question)
                    except ValueError as e:
                        logger.error(
                            'An error {} has occurred during parsing file: {}'.format(
                                str(e), self.open_file.name
                            )
                        )

                current_question_dict = self.initialize_step_question_dict()

            current_question_dict[key] = self._extract_entity_from_text()

            line = self.open_file.readline()

        if current_question_dict['question']:
            try:
                quiz_question = QuizQuestion(**current_question_dict)
                self.list_of_parsed_questions.append(quiz_question)
            except ValueError as e:
                logger.error(
                    'An error {} has occurred during parsing file: {}'.format(
                        str(e), self.open_file.name
                    )
                )

    def initialize_step_question_dict(self):
        current_question_dict = {
            key: '' for key in QuizQuestionsFileParser.rx_dict.keys()
        }
        return current_question_dict

    def _parse_line(self, text_line):
        for key, rx in QuizQuestionsFileParser.rx_dict.items():
            match = rx.search(text_line)
            if match:
                return key
        return None

    def _extract_entity_from_text(self):
        line = self.open_file.readline()
        question_text = []

        while line.strip():
            question_text.append(line)
            line = self.open_file.readline()
        return ''.join(question_text)
