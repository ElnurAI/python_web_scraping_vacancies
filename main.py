# import libraries
from googletrans import Translator
from datetime import date
from bs4 import BeautifulSoup
import requests
import re
from database import Database
from time import sleep

class Vacancies(Database):

    def __init__(self):
        super(Vacancies, self).__init__()

    @staticmethod
    def csoup(url):
        html_page = requests.get(url)
        return BeautifulSoup(html_page.text, 'html.parser')

    @staticmethod
    def completed_link(site_link, link):
        if 'Undefined' in link:
            return 'Undefined'
        elif 'https://' in link:
            return link
        else:
            return site_link + link

    @staticmethod
    def text_language(text, dest='az'):

        language = ''
        try:
            translator = Translator(service_urls=['translate.google.com'])
            translated = translator.translate(text, dest=dest)
            language = translated.src
        except Exception as error:
            print(error)
            language = '-'

        return language

    @staticmethod
    def extract_numbers(text, join_indicator=''):

        number_list = []
        regular_exp = '[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+'

        if re.search(regular_exp, text) is not None:
            for catch in re.finditer(regular_exp, text):
                number_list.append(catch[0])

        return join_indicator.join(number_list)

    @staticmethod
    def dictionary_nullvalues(list):

        dic = {}
        for column in list:
            dic[column] = None

        return dic

    def convert_date_format(self, months, start_date, end_date):

        start_date_split = start_date.split(" ")
        end_date_split = end_date.split(" ")

        s_day = int(start_date_split[0])
        s_month = months[start_date_split[1].lower()]

        e_day = int(end_date_split[0])
        e_month = months[end_date_split[1].lower()]
        s_year = date.today().year

        if e_month < s_month:
            e_year = date.today().year + 1
        else:
            e_year = date.today().year

        s_date = date(s_year, s_month, s_day)
        e_date = date(e_year, e_month, e_day)

        return s_date, e_date

    def run(self):
        dic_keys = ['site_name', 'ad_link', 'ad_id', 'ad_language', 'company_name', 'post_title', 'hr_contact',
                    'start_date', 'end_date', 'visitor_number', 'city', 'position', 'work_experience', 'salary',
                    'currency', 'job_mode', 'work_area', 'category', 'about_job']

        months = {'yanvar': 1, 'fevral': 2, 'mart': 3, 'aprel': 4, 'may': 5, 'i̇yun': 6,
                  '̇i̇yul': 7, 'avqust': 8, 'sentyabr': 9, 'oktyabr': 10, 'noyabr': 11, 'dekabr': 12}

        change_categories_name = {'Şəhər': 'city', 'Vəzifə': 'position', 'İş stajı': 'work_experience', 'Sahə': 'work_area',
                                  'Əmək haqqı AZN': 'salary', 'İş rejimi': 'job_mode', 'Kateqoriya': 'category'}

        change_job_mode = {'full-time': 'Tam-ştat', 'part-time': 'Yarım-ştat', 'intership': 'Təcrübəçi',
                           'remote': 'Uzaqdan', 'freelance': 'Frilans'}

        site_link = 'https://www.hellojob.az'
        url = self.completed_link(site_link, '/vakansiyalar')
        all_ads = []

        # ink_page = 0
        # page_num = 1

        while True:

            # ink_page += 1
            # if ink_page > page_num:
            #     break

            page = self.csoup(url)

            container = page.find_all(attrs={"class": "vacancies__item vacancies__item_new"})
            # ink_ad = 0
            # ad_num = 2
            for c in container:

                # ink_ad += 1
                # if (ink_ad > ad_num): break

                ad_dic = self.dictionary_nullvalues(dic_keys)

                link = self.completed_link(site_link, c.get('href'))

                print(link)

                soup = self.csoup(link)

                content = soup.find_all(attrs={"class": "resume__block"})

                if content:
                    content_text = content[2].text.replace('\n', ' ')
                    ad_language = self.text_language(content_text)

                if ad_language != "az" and ad_language != '-':
                    continue

                ad_dic['site_name'] = site_link[site_link.index('//') + 2:]
                ad_dic['ad_link'] = link
                ad_dic['ad_language'] = ad_language

                post_title = soup.find(attrs={"class": "resume__header__name"})

                if post_title:
                    ad_dic['post_title'] = post_title.text.strip()

                company_name = soup.find(attrs={"class": "resume__header__speciality"})

                if company_name:
                    ad_dic['company_name'] = company_name.text.strip().strip()

                contact_container = soup.find(attrs={"class": "contact"})
                ad_id = contact_container.find(attrs={"class": "contact__top"}).find("h4")

                if ad_id:
                    ad_dic['ad_id'] = int(self.extract_numbers(ad_id.text.strip()))

                hr_email = soup.find(attrs={"class": "btn btn-apply email d-none"})

                if hr_email:
                    hr_contact = hr_email.text.strip()
                else:
                    hr_contact = soup.find(attrs={"class": "btn btn-apply"})

                    if hr_contact:
                        hr_contact = hr_contact.get('href')

                if hr_contact:
                    ad_dic['hr_contact'] = hr_contact

                contact_bottom = contact_container.find(attrs={"class": "contact__bottom"})
                start_date = contact_bottom.find_all(attrs={"class": "resume__item__text"})
                end_date = contact_bottom.find_all(attrs={"class": "resume__item__text"})
                visitor_number = contact_bottom.find_all(attrs={"class": "resume__item__text"})

                if start_date and end_date:
                    s_date = start_date[0].find("h4").text
                    e_date = end_date[1].find("h4").text
                    ad_dic['start_date'], ad_dic['end_date'] = self.convert_date_format(months, s_date, e_date)

                if visitor_number:
                    ad_dic['visitor_number'] = int(visitor_number[2].find("h4").text)

                info_container = soup.find_all(attrs={"class": "resume__block"})[1].find_all(attrs={"class": "col-md-6"})

                # The loop takes general information about job due to the categories.
                # Categories: city, position, work_experience, salary, job_mode, work_area, and category.
                for info in info_container:

                    temp = info.find(attrs={"class": "resume__item__text"})

                    if temp:
                        name = temp.find("p").text.strip()
                        text = temp.find("h4").text.strip()

                        if name == 'İş rejimi':
                            if text.lower() in change_job_mode.keys():
                                text = change_job_mode[text.lower()]

                        if name == 'Əmək haqqı AZN':
                            text = self.extract_numbers(text.strip(), '-')

                        ad_dic[change_categories_name[name]] = text.strip()

                if ad_dic['salary'] is not None:
                    ad_dic['currency'] = 'AZN'

                job_info_container = soup.find_all(attrs={"class": "resume__block"})[2]

                # The loop takes information about job description.
                # Description: about company, requirements, responsibilities.
                about_job_desc = ''
                temporary_job_desc = ''
                for info in job_info_container:

                    if info.name == 'hr':
                        break
                    elif info.name == 'h3':
                        pass
                    elif (info.name == 'ul') or (info.name == 'ol'):
                        for elem in info.find_all('li'):
                            if elem.text.strip() != '':

                                if temporary_job_desc != '':
                                    temporary_job_desc += ' ' + elem.text.strip()
                                else:
                                    temporary_job_desc = elem.text.strip()

                        if about_job_desc != '':
                            about_job_desc += ' ' + temporary_job_desc
                        else:
                            about_job_desc = temporary_job_desc
                    else:
                        if info.text.strip() != '':

                            if about_job_desc != '':
                                about_job_desc += ' ' + info.text.strip()
                            else:
                                about_job_desc = info.text.strip()

                ad_dic['about_job'] = about_job_desc

                if ad_dic['ad_language'] == 'az':
                    all_ads.append(ad_dic)

                print(ad_dic)

                self.run_database([ad_dic])

            next_page = page.find(attrs={"aria-label": "Next"})

            # self.run_database(all_ads)

            if next_page:
                url = self.completed_link(site_link, next_page.get('href'))
                print(url)
            else:
                print('finished')
                break

if __name__ == '__main__':
    vacancy = Vacancies()
    vacancy.run()