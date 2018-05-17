import os
import sys
import unittest

from pyquery import PyQuery as pq

sys.path.append('..')

from exone_parser import ExoneParser

from unittest.mock import patch
from utils import prepare_logs_dir

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA_DIR_NAME = 'data'
TEST_DATA_DIR = os.path.join(CURRENT_DIR, TEST_DATA_DIR_NAME)

LOGS_DIR = 'logs'
LOGS_PATH = os.path.join(CURRENT_DIR, LOGS_DIR)

LIST_PAGE_FILENAME = 'test_list.html'
LIST_PAGE_FILEPATH = os.path.join(TEST_DATA_DIR, LIST_PAGE_FILENAME)
VACANCY_PAGE_FILENAME = 'test_vacancy.html'
VACANCY_PAGE_FILEPATH = os.path.join(TEST_DATA_DIR, VACANCY_PAGE_FILENAME)

prepare_logs_dir(LOGS_PATH)


class ParserTestCase(unittest.TestCase):
    """
    Parser tests
    """
    TEST_LIST = [
            {'vacancy_type': 'Vollzeit',
             'vacancy_location': 'Giengen-Sachsenhausen',
             'vacancy_title': 'Elektronik-Montierer/in',
             'vacancy_url': 'https://www.exone.de/jm/web/tool/jobmanager/'
                            'apply.php?sttyp=1&arst=detail&id=85',
             'vacancy_id': '85'}]

    def setUp(self):
        self.parser = ExoneParser()

    def test_get_vacancies(self):
        page = pq(filename=LIST_PAGE_FILEPATH)
        with patch.object(ExoneParser, '_get_page',
                          return_value=page):
            self.parser._get_vacancies()
            self.assertEqual(len(self.parser.vacancy_list), 6)

    def test_get_description(self):
        page = pq(filename=VACANCY_PAGE_FILEPATH)
        self.parser.vacancy_list = self.TEST_LIST
        with patch.object(ExoneParser, '_get_page',
                          return_value=page):
            self.parser._get_descriptions()
            self.assertNotEqual("",self.parser.vacancy_list[0]['description'])

    def test_get_id(self):
        id = self.parser._get_job_id(self.TEST_LIST[0]['vacancy_url'])
        self.assertEqual(id, '85')


if __name__ == '__main__':
    unittest.main()
