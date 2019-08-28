# from bs4 import BeautifulSoup
# from urllib.request import urlopen
import os
import django
import requests
import json
# import csv
import multiprocessing
import time
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from questionFilter.models import *


class LeetCodeCrawler(object):
    def __init__(self, user, password):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        self.session = requests.Session()
        self.base_url = 'https://leetcode.com/'
        self.is_premium = False
        self.headers = {'User-Agent': self.user_agent}
        r = self.session.get(self.base_url, headers=self.headers)
        csrftoken = re.search(r'(?<=csrftoken=).*?(?=;)', r.headers['Set-Cookie']).group(0)
        self.headers['x-csrftoken'] = csrftoken
        self.max_retry_time = 10
        self.is_login = self.login(user, password)
        if self.is_login:
            print('login successfully!')
        else:
            print('login failed!')

    def login(self, user, password):
        current_headers = self.headers.copy()
        login_url = 'https://leetcode.com/accounts/login/'
        login_info = {'csrfmiddlewaretoken':current_headers['x-csrftoken'],
             'login':'XX',
              'password':'XX',
              'next':'/problems'
             }
        current_headers['referer'] = 'https://leetcode.com/accounts/login/'

        query = {'operationName': "globalData",
                'query': '''query globalData {
                    isCurrentUserAuthenticated
                    isPremium
                }'''
            }
        verify = None
        retry_time = 0
        while verify is None and retry_time < self.max_retry_time:
            try:
                retry_time += 1
                print('retry: ',retry_time)
                log = self.session.post(login_url, headers = current_headers, timeout=2, data = login_info, allow_redirects = False)
                current_headers['content-type'] = 'application/json'
                verify = self.session.post('https://leetcode.com/graphql', headers = current_headers, timeout=2, data=json.dumps(query)).json()
            except:
                pass
        if verify is None:
            print("Something Wrong")
            return False
        else:
            self.is_premium = verify['data']['isPremium']
            return verify['data']['isCurrentUserAuthenticated']

    def get_questions_list(self):
        all_questions_url = 'https://leetcode.com/api/problems/all/'
        all_questions = self.session.get(all_questions_url, headers=self.headers)
        return all_questions.json()

    def save_to_db(self, detail, paid_only, frequency):
        detail = detail['data']
        question = detail['question']

        question_slug = question['questionTitleSlug']
        front_id = question['questionFrontendId']
        content = question['content']
        name = question['questionTitle']
        difficulty = question['difficulty']
        stats = eval(question['stats'])
        total_accept = stats['totalAcceptedRaw']
        total_submission = stats['totalSubmissionRaw']
        accept_rate = stats['acRate'][:-1]
        like = question['likes']
        dislike = question['dislikes']

        # slimilars = question['similarQuestions']
        # company_tags = question['companyTags']
        # company_stats = question['companyTagStats']
        db_question = Question.objects.get_or_create(question_slug = question_slug,
                                                    front_id=front_id,
                                                    content=content,
                                                    name=name,
                                                    difficulty=difficulty,
                                                    total_accept=total_accept,
                                                    total_submission=total_submission,
                                                    accept_rate=accept_rate,
                                                    paid_only=paid_only,
                                                    like=like,
                                                    dislike=dislike,
                                                    frequency=frequency)


        if db_question[1]:
            db_question[0].save()
        print(db_question)
        # db_companies = question['companyTags']
        company_tags = json.loads(question['companyTagStats']).values()
        # if len(db_companies) > 0:
            # for company in db_companies:
            #     company_slug = company['slug']
            #     name = company['name']
            #     db_company = Company.objects.get_or_create(company_slug=company_slug,
                                                        # name=name)
    #         # db_company.save()
    #
        for block in company_tags:
            for company_tag in block:
                company_slug = company_tag['slug']
                name = company_tag['name']
                db_company = Company.objects.get_or_create(company_slug=company_slug,
                                                        name=name)
                if db_company[1]:
                    db_company[0].save()
                vote_count = company_tag['timesEncountered']
                db_company_tag = CompanyTag.objects.get_or_create(company_slug=db_company[0],
                                                                    question_slug=db_question[0],
                                                                    vote_count=vote_count)
                if db_company_tag[1]:
                    db_company_tag[0].save()
        algorithm_tags = question['topicTags']
        for algorithm_tag in algorithm_tags:
            algorithm_slug = algorithm_tag['slug']
            name = algorithm_tag['name']
            db_algorithm = Algorithm.objects.get_or_create(algorithm_slug=algorithm_slug,
                                                            name=name)
            if db_algorithm[1]:
                db_algorithm[0].save()
            db_algorithm_tag = AlgorithmTag.objects.get_or_create(algorithm_slug=db_algorithm[0],
                                                                    question_slug=db_question[0])
            if db_algorithm_tag[1]:
                db_algorithm_tag[0].save()

        similars = json.loads(question['similarQuestions'])
        for similar in similars:
            tar_question_slug = similar['titleSlug']
            tar_difficulty = similar['difficulty']
            try:
                db_tar_question = Question.objects.get(question_slug=tar_question_slug)
                db_similar1 = Similar.objects.get_or_create(cur_question_slug=db_question[0],
                                                            tar_question_slug=db_tar_question,
                                                            tar_difficulty=tar_difficulty)
                if db_similar1[1]:
                    db_similar1[0].save()
                db_similar2 = Similar.objects.get_or_create(cur_question_slug=db_tar_question,
                                                            tar_question_slug=db_question[0],
                                                            tar_difficulty=difficulty)
                if db_similar2[1]:
                    db_similar2[0].save()
            except Question.DoesNotExist:
                continue


    def get_detail(self, slug, paid_only, frequency):
        query_url = 'https://leetcode.com/graphql'
        current_headers = self.headers.copy()
        current_headers['referer'] = self.base_url + '/problems/' + slug
        current_headers['content-type'] = 'application/json'
        query = {'operationName': "getQuestionDetail",
                 'variables': {'titleSlug': slug},
                 'query': '''query getQuestionDetail($titleSlug: String!) {
                    question(titleSlug: $titleSlug) {
                        questionId
                        questionFrontendId
                        questionTitle
                        questionTitleSlug
                        content
                        difficulty
                        stats
                        similarQuestions
                        categoryTitle
                        topicTags {
                                name
                                slug
                        }
                        # companyTags {
                        #   name
                        #   slug
                        # }
                        companyTagStats
                        likes
                        dislikes
                    }
                }'''
                 }

        detail = None
        retry_time = -1
        while detail is None and retry_time < self.max_retry_time:
            try:
                retry_time += 1
                if retry_time > 0:
                    print(retry_time)
                detail = self.session.get(query_url, data=json.dumps(query), headers=current_headers).json()
                temp = detail['data']['question']

            except:
                pass
        self.save_to_db(detail, paid_only, frequency)
        print(temp['questionFrontendId'], temp['questionTitleSlug'])

        return detail

    # Multithreading version
    def get_all_details1(self):
        questions_list = self.get_questions_list()['stat_status_pairs']
        start = time.time()
        pool = multiprocessing.Pool()
        for question in questions_list:
            print(question['stat']['frontend_question_id'])
            paid_only = question['paid_only']
            frequency = question['frequency']
            if self.is_premium or not paid_only:
                pool.apply_async(self.get_detail, (question['stat']['question__title_slug'], paid_only, frequency))
        #                 self.getDetail(question['stat']['question__title_slug'])
        pool.close()
        pool.join()
        print("Multiple Processing Version: ", time.time() - start)

    # Sequential version
    def get_all_details2(self):
        questions_list = self.get_questions_list()['stat_status_pairs']
        start = time.time()
        for question in questions_list:
            paid_only = question['paid_only']
            frequency = question['frequency']
            if self.is_premium or not paid_only:
                self.get_detail(question['stat']['question__title_slug'], paid_only, frequency)

        print("Sequential Version: ", time.time() - start)


if __name__ == '__main__':
    crawler = LeetCodeCrawler(1,2)
    # l = crawler.get_questions_list()
    # print(l)
    # crawler.login(1,2)
    # detail = crawler.get_detail('two-sum', False, 0)
    # detail = crawler.get_detail('3sum', False)
    # detail = crawler.get_detail('reordered-power-of-2', False)

    # print(detail['data']['question'])
    crawler.get_all_details1()
    # print(l['stat_status_pairs'][0])
