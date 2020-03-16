import json
import time
import random
from json import JSONDecodeError

import requests
CHROME_WIN_UA = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
BASE_URL = 'https://www.instagram.com/'
STORIES_UA = 'Instagram 123.0.0.21.114 (iPhone; CPU iPhone OS 11_4 like Mac OS X; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/605.1.15'
LOGIN_URL = BASE_URL + 'accounts/login/ajax/'
RETRY_DELAY = 5
CONNECT_TIMEOUT = 90
MAX_RETRY_DELAY = 60
MAX_RETRIES = 5
import os
import re
import instaloader


class instagram:
    def __init__(self,**kwargs):


        self.default_attr = dict(username='', usernames=[], filename=None,
                            login_user=None, login_pass=None,
                            followings_input=False, followings_output='profiles.txt',
                            destination='./', logger=None, retain_username=False, interactive=False,
                            quiet=False, maximum=0, media_metadata=False, profile_metadata=False, latest=False,
                            latest_stamps=False, cookiejar=None, filter_location=None, filter_locations=None,
                            media_types=['image', 'video', 'story-image', 'story-video'],
                            tag=False, location=False, search_location=False, comments=False,
                            verbose=0, include_location=False, filter=None, proxies={}, no_check_certificate=False,
                            template='{urlname}', log_destination='')
        allowed_attr = list(self.default_attr.keys())
        self.default_attr.update(kwargs)
        self.start_time = 0
        self.start_time1 = 0
        for key in self.default_attr:
            if key in allowed_attr:
                self.__dict__[key] = self.default_attr.get(key)
        self.instaloader = instaloader.Instaloader()
        self.instaloader.login(self.default_attr['login_user'], self.default_attr['login_pass'])
        self.session = requests.Session()
        self.session.headers = {'user-agent': CHROME_WIN_UA}
        self.cookiejar = None

        self.cookies = None
        self.authenticated = False
        self.logged_in = False
        self.last_scraped_filemtime = 0
        self.quit = False

    def authenticate_with_login(self):
        self.session.headers.update({'Referer': BASE_URL, 'user-agent': STORIES_UA})
        req = self.session.get(BASE_URL)

        self.session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})

        # print(self.session)
        login_data = {'username': self.login_user, 'password': self.login_pass}
        login = self.session.post(LOGIN_URL, data=login_data, allow_redirects=True)

        self.session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        self.cookies = login.cookies
        login_text = json.loads(login.text)
        print(login_text)
        if login_text.get('authenticated') and login.status_code == 200:
            self.authenticated = True
            self.logged_in = True
            self.session.headers.update({'user-agent': CHROME_WIN_UA})
            self.rhx_gis = ""


    # def setLikes(self, username):
    #     """Generator for followings."""
    #     st = json.dumps(self.get_shared_data(username))
    #
    #     keys = set(re.findall(r'\d{19}',st))
    #     print(keys)
    #     for key in keys[:1]:
    #         self.session.post('https://www.instagram.com/web/likes/'+key+'/like/')
    #         print('Поставили like для '+key)
    #         time.sleep(random.randint(1,10))

    def get_username_from_id(self, id):
        return instaloader.Profile.from_id(self.instaloader.context, id).username

    def get_id_from_username(self, username):
        return instaloader.Profile.from_username(self.instaloader.context, username).userid

    def get_followers_from_id(self, id):
        return instaloader.Profile.from_id(self.instaloader.context, id).get_followers()

    def get_followers_from_username(self, username):
        return instaloader.Profile.from_username(self.instaloader.context, username).get_followers()

    def get_is_follow(self, username):
        return instaloader.Profile.from_username(self.instaloader.context, username).followed_by_viewer

    def set_likes(self,usernames,num_likes_of_user = 1,counts_likes_hour = 60,count_follow_hour = 30,block = 7200):
        times_sleep = 3600/counts_likes_hour
        times_sleep1 = 3600 / count_follow_hour
        for username in usernames:
            gen = self.get_followers_from_username(username)
            per1 = True

            while per1:
                if (time.time() - self.start_time) > block and (time.time() - self.start_time1) > block:
                    try:
                        user = next(gen)
                        posts = user.get_posts()
                    except StopIteration:
                        per1 = False
                    per = True
                    it = 0
                    while per:
                        try:
                            if num_likes_of_user==it:
                                per = False
                            else:
                                post = next(posts)
                                if not post.viewer_has_liked and (time.time()-self.start_time)>block:
                                    self.start_time = 0
                                    d = True
                                    while d:
                                        try:
                                            a = self.session.post('https://www.instagram.com/web/likes/' + str(post.mediaid) + '/like/')

                                            print('Лайнкнули ',user, post.mediaid, a.json())
                                            time.sleep(random.randint(times_sleep/2 - 10, times_sleep/2 + 10))
                                            it += 1
                                            d = False
                                        except JSONDecodeError:
                                            self.start_time = time.time()
                                            d = False
                                            print('Заблокировли лайки')

                        except StopIteration:
                            per = False


                    if not self.get_is_follow(user.username) and (time.time()-self.start_time1)>block:
                        self.start_time1 = 0
                        d1 = True
                        while d1:
                            try:
                                a1 = self.session.post('https://www.instagram.com/web/friendships/'+str(user.userid)+'/follow/',allow_redirects=False)
                                print('подписались на',user)
                                time.sleep(random.randint(times_sleep1/2 - 10, times_sleep1/2 + 10)  )
                                d1 = False
                            except JSONDecodeError:
                                self.start_time1 = time.time()
                                d1 = False
                                print('Заблокировли подписки')
                                # print('прошло ',str(time.time()-self.start_time))




login = os.environ.get('LOGIN')
password = os.environ.get('PASSWORD')


a = instagram(login_user = login,login_pass = password)
a.authenticate_with_login()
a.set_likes(['pod_nebom_ukg'])
# print(a.get_is_follow('pod_nebom_ukg'))
