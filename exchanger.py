import os
import sys
import json
import logging
import requests

from splinter import Browser

from utils import prepare_logs_dir

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))

"""Settings for local testing on Linux/Mac with Chrome driver"""

LINUX_PLATFORM = 'linux'
MAC_PLATFORM = 'darwin'

WEB_DRIVERS = {
    LINUX_PLATFORM: 'chromedriver_linux_x64',
    MAC_PLATFORM: 'chromedriver_darwin'
}

try:
    DRIVER_PATH = os.path.join(CURRENT_PATH, 'drivers',
                               WEB_DRIVERS[sys.platform])
except:
    raise Exception

prepare_logs_dir()

logging.basicConfig(filename='logs/exchanger.log', level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s '
                           '%(message)s',
                    datefmt='%d-%m-%y %H:%M')


class Exchanger:
    """
    Class to apply for job with user data
    """
    DOWNLOADS_DIR = 'downloads'

    def __init__(self, vacancy_url, user_data):
        """
        Init class
        :param vacancy_url: url of vacancy page
        :param user_data: dict with user data
        """
        self.browser = self._setup_browser()
        self.vacancy_url = vacancy_url
        self.user_data = user_data

    @staticmethod
    def _setup_browser():
        """
        Prepare splinter browser
        :return: Browser object
        """
        logging.info('##### Prepare browser #####')
        options = {'executable_path': DRIVER_PATH, 'headless': True}
        return Browser('chrome', **options)

    def _open_page(self):
        """
        Visit vacancy page and apply for a job
        """
        logging.info('Open vacancy page {}'.format(self.vacancy_url))
        self.browser.visit(self.vacancy_url)
        self.browser.check("agree_apply")
        self.browser.find_by_name('btn_apply').click()

    def _fill_inputs(self):
        """
        Fill required fields (1st step)
        """
        logging.info('Fill inputs')
        self.browser.fill('appl_vorname',
                          self.user_data['first_name'])
        self.browser.fill('appl_nachname',
                          self.user_data['last_name'])
        self.browser.fill('appl_telefon_mobil', self.user_data['phone'])
        self.browser.fill('appl_email', self.user_data['email'])
        self.browser.fill('appl_geburtstag', self.user_data['birthday'])
        self.browser.fill('appl_strasse', self.user_data['street'])
        self.browser.fill('appl_plz', self.user_data['postal_code'])
        self.browser.fill('appl_ort', self.user_data['city'])
        self.browser.fill('appl_geburtsort', self.user_data['city'])
        self.browser.fill('appl_staatsangehoerigkeit', 'JobUFO')
        self.browser.fill('appl_nationalitaet', 'JobUFO')
        self.browser.fill('appl_telefon_privat', self.user_data['phone'])

    def _fill_texts(self):
        """
        Fill textarea (2nd step)
        :return: 
        """
        fields = self.browser.find_by_tag('textarea')
        for field in fields:
            field.value = "JobUFO Videobewerbung"

    def _download_file(self, file_url):
        """
        Download file
        :param file_url: url to file
        :return: str file path
        """
        logging.info('Download cv file')
        file_url = file_url
        r = requests.get(file_url, allow_redirects=True)
        filename = file_url.rsplit('/', 1)[1]
        downloads_dir = os.path.join(CURRENT_PATH, self.DOWNLOADS_DIR)

        # create directory to save downloaded file if it does not exists
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)
        file_path = os.path.join(downloads_dir, filename)
        try:
            open(file_path, 'wb').write(r.content)
        except Exception as e:
            logging.info('Can not download file: {}'.format(str(e)))
        return file_path

    def _upload_files(self):
        """
        Upload files
        """
        # need to clear file fields if some files was uploaded before
        for i in range(4):
            if self.browser.is_element_present_by_name('file_{}'.format(i)):
                self.browser.check('file_{}'.format(i))
        if self.browser.is_element_present_by_name('btn_file_delete'):
            self.browser.find_by_name('btn_file_delete').click()

        file_path = self._download_file(self.user_data['cv_path'])
        img_path = self._download_file(self.user_data['photo'])
        logging.info('Try to attach file')
        try:
            self.browser.attach_file('upload_1', img_path)
            self.browser.attach_file('upload_2', file_path)
            self.browser.attach_file('upload_3', file_path)
            self.browser.attach_file('upload_4', file_path)
            self.browser.find_by_name('btn_upload_all').click()
        except Exception as e:
            logging.info('Can not upload file: {}'.format(str(e)))

    def run(self):
        """
        Run process of applying job
        """
        self._open_page()
        self._fill_inputs()
        self.browser.find_by_name('btn_next_1').click()
        self._fill_texts()
        self.browser.find_by_name('btn_next_2').click()
        self._upload_files()
        self.browser.find_by_name('btn_next_3').click()
        logging.info('##### Exchange completed #####')


if __name__ == "__main__":
    url = 'https://www.exone.de/jm/web/tool/jobmanager/apply.php?' \
          'sttyp=1&arst=detail&id=85'
    data = json.load(open('test_user_data.json'))
    parser = Exchanger(user_data=data, vacancy_url=url)
    parser.run()
