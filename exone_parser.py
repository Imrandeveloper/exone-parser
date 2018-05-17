import os
import logging

from pyquery import PyQuery as pq
from urllib import parse
from lxml import etree

from utils import prepare_logs_dir


# prepare all necessary for logs
prepare_logs_dir()
logging.basicConfig(filename='logs/parser.log', level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%d-%m-%y %H:%M')


class ExoneParser:
    """
     Exone website parser
    """
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
    # Config path for xml export
    OUTPUT_DIR = "parsed_xml"
    OUTPUT_FILENAME = "vacancies.xml"
    DIR_TO_EXPORT = os.path.join(CURRENT_DIR, OUTPUT_DIR)
    # the maximum number of attempts to obtain a response,
    # in case the server responded with an error
    ATTEMPTS_COUNT = 3

    # Url  to get vacancy list
    MAIN_URL = "https://www.exone.de/jm/web/tool/jobmanager/apply.php?sttyp=1"
    # Base url to get vacancy
    BASE_VACANCY_URL = "https://www.exone.de/jm/web/tool/jobmanager/apply.php"

    # Types of work depending on time
    JOBS_KIND = {
        'Vollzeit': "FULL_TIME",
        'Teilzeit': "PART_TIME",
    }

    def __init__(self):
        """
        Init class
        """
        self.vacancy_list = []

    @staticmethod
    def _get_job_id(link):
        """
        Fetching job id from vacancy url
        :param link: vacancy url
        :return: Job ID
        """
        try:
            return parse.parse_qs(parse.urlparse(link).query)['id'][0]
        except Exception as e:
            logging.info(
                "Can not get identifier from url {} {}".format(link, str(e)))
            return ""

    def _get_page(self, url):
        """
        Trying to get page content from url
        :param url: page url
        :return: page content as PQuery object
        """
        current_attempt = 1
        res = None
        while True:
            logging.info("Trying to get page {}, attempts count: {}"
                         ''.format(url, self.ATTEMPTS_COUNT))
            try:
                res = pq(url=url)
            except Exception as e:
                logging.info("Cannot get page {} \nError: {}"
                             ''.format(url, e))
            if (current_attempt == self.ATTEMPTS_COUNT) or res:
                break
            current_attempt += 1
        return res

    def _get_vacancies(self):
        """
        Getting vacancy list from main page.
        :return: True: if vacancies has been taken,False: if something
         went wrong. All errors will be in logs.
        """
        page = self._get_page(self.MAIN_URL)
        if page:
            logging.info("Parsing vacancy list")
            # Find objects with vacancies on page
            vacancies = page.find('div[class=ex-job-list-item]')
            logging.info("Vacancies count : {}".format(len(vacancies)))
            # parse vacancies step by step
            for vacancy in vacancies.items():
                vacancy_url = self.BASE_VACANCY_URL + \
                              vacancy.find('a').attr('href')
                self.vacancy_list.append({
                    'vacancy_type':
                        vacancy.find('b').eq(0).text().split(' ')[0],
                    'vacancy_location':
                        vacancy.find('b').eq(1).text(),
                    'vacancy_title': vacancy.find('h4').text(),
                    'vacancy_url': vacancy_url,
                    'vacancy_id': self._get_job_id(vacancy_url)
                })
            if len(self.vacancy_list)>0:
                return True
        else:
            logging.info("No page received. Revocation")
        logging.info('No vacancies found')
        return False

    def _get_descriptions(self):
        """
        Getting vacancy descriptions from vacancies page using
        prepared vacancy list
        :return: True: if all descriptions has been taken
        False : if parser has not found description on page, program will be
        stopped
        """
        for vacancy in self.vacancy_list:
            vacancy_page = self._get_page(vacancy['vacancy_url'])
            if vacancy_page:
                logging.info("Parsing description of vacancy id: {}"
                             .format(vacancy['vacancy_id']))
                description = \
                    vacancy_page.find('div[class=ex-job-description]').text()
                if description == "":
                    logging.info("Cannot get vacancy description. Revocation")
                    return False
                else:
                    vacancy.update({'description': description})
            else:
                logging.info("Cannot get vacancy details page. Revocation")
                return False
        return True

    def _export_to_xml(self):
        """
        Export vacancies to xml file
        :return: xml file path
        """
        root = etree.Element('vacancies')
        for data in self.vacancy_list:
            vacancy = etree.SubElement(root, 'position')
            etree.SubElement(vacancy, 'link').text = data["vacancy_url"]
            etree.SubElement(vacancy, 'identifier').text = data["vacancy_id"]
            etree.SubElement(vacancy, 'title').text = data["vacancy_title"]
            etree.SubElement(vacancy, 'start_date')
            try:
                etree.SubElement(vacancy, 'kind').text = \
                    self.JOBS_KIND[data["vacancy_type"]]
            except Exception as e:
                logging.info("Can't get kind of vacancy  {}".format(str(e)))
                etree.SubElement(vacancy, 'kind')
            etree.SubElement(vacancy, 'description').text = \
                etree.CDATA(data["description"])
            etree.SubElement(vacancy, 'top_location').text = data[
                "vacancy_location"].split('-')[0]
            locations = etree.SubElement(vacancy, 'locations')
            try:
                etree.SubElement(locations, 'location').text = data[
                                "vacancy_location"].split('-')[1]
            except:
                etree.SubElement(locations, 'location')
            etree.SubElement(vacancy, 'images')
            company = etree.SubElement(vacancy, 'company')
            etree.SubElement(company, 'name').text = "Exone"
            address = etree.SubElement(company, 'address')
            etree.SubElement(address, 'street')
            etree.SubElement(address, 'zip')
            etree.SubElement(address, 'city').text = data[
                "vacancy_location"].split('-')[0]
            etree.SubElement(vacancy, 'contact_email').text = \
                'fallback@jobufo.com'

        # create directory to save parsed xml if it does not exists
        if not os.path.exists(self.DIR_TO_EXPORT):
            os.makedirs(self.DIR_TO_EXPORT)

        filepath = os.path.join(self.DIR_TO_EXPORT, self.OUTPUT_FILENAME)

        tree = etree.ElementTree(root)
        tree.write(filepath, pretty_print=True, xml_declaration=True,
                   encoding='utf-8')
        return filepath

    def run(self):
        """
        The main function that controls the rest
        :return:
        """
        if self._get_vacancies():
            if self._get_descriptions():
                self._export_to_xml()


if __name__ == "__main__":
    parser = ExoneParser()
    parser.run()
