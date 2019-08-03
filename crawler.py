# -*- coding=utf-8 -*-
# author: Chi-zhan Zhang
# date:2019/7/27
# func: twitter spider demo

import json
import os
import shutil
import requests
import time
import threading
import datetime

from id_collection import create_api, create_user_agent


class TwitterCrawler(object):
    def __init__(self, since_id=None, clean_dir=False):
        # TODO: change the proxy value by your own proxy
        self.proxy = ''
        # TODO: change the QUERY value by your own QUERY
        self.QUERY = ''

        self.result_text_dir = './temp_data'
        self.picture_dir = './pictures'
        self.all_result_file = os.path.join(self.result_text_dir, 'all_result.json')
        self.tweets_with_picture_file = os.path.join(self.result_text_dir, 'tweets_with_picture.json')
        self.updating_all_result_file = os.path.join(self.result_text_dir, 'updating_all_result.json')
        self.picture_downloaded_error_file = os.path.join(self.result_text_dir, 'picture_download_error_tweets.json')
        self.log_path = './log.txt'
        self.MAX_TWEETS = 10000
        self.COUNT_PER_QUERY = 100
        self.tweet_downloaded_count = 0
        self.tweet_refined_count = 0
        self.api = create_api(proxy=self.proxy)
        self.since_id = since_id
        """Thread setting"""
        self.lock = threading.RLock()
        self.MAX_THREADS = 10
        self.working_threads = 0
        self.finished_threads = 0
        """Dir initialization"""
        if clean_dir:
            self._clean_dir()
        if not os.path.isdir(self.picture_dir):
            os.mkdir(self.picture_dir)
        if not os.path.isdir(self.result_text_dir):
            os.mkdir(self.result_text_dir)
        """Update status, if since_id is not None, it is considered updating status"""
        if since_id:
            if os.path.isfile(self.updating_all_result_file):
                os.remove(self.updating_all_result_file)
            self.all_result_file = self.updating_all_result_file

    def _clean_dir(self):
        """ func:   remove tem_data dir and picture dir"""
        if os.path.isdir(self.picture_dir):
            shutil.rmtree(self.picture_dir)
        if os.path.isdir(self.result_text_dir):
            shutil.rmtree(self.result_text_dir)
        self.log_info("Successfully cleaned temp_data dir and picture dir!")

    def _save_all_result(self, search_results):
        """ func:   save all results of one api.search()
            :arg    search_results is the return of api.search()
        """
        with open(self.all_result_file, 'a', encoding='utf8') as f:
            for i, one_tweet in enumerate(search_results):
                json.dump(one_tweet._json, f, ensure_ascii=False)
                f.write('\n')
        self.tweet_downloaded_count += len(search_results)
        self.log_info('Total downloaded {:^6d} tweets'.format(self.tweet_downloaded_count))

    def _download_picture(self, url, picture_id, picture_dir):
        """ func:   download a picture of a tweet
            :arg    url is the picture link
                    picture_id is the tweet id
                    picture_dir is the dir storing all of the downloaded pictures
            :return if picture is successfully downloaded, return True; else, return False
        """
        proxies = {'http': self.proxy, 'https': self.proxy}
        filename = os.path.join(picture_dir, str(picture_id) + url[-4:])
        try:
            r = requests.get(url, headers={'User-Agent': create_user_agent()}, proxies=proxies)
            r.raise_for_status()
            with open(filename, 'wb') as f:
                f.write(r.content)
            return True
        except:
            self.log_info("Download picture wrong: %s" % url)
            return False

    def _save_one_refined_tweet(self, tweet):
        """ func:   Save the id, full_text and picture_url of one tweet having at least one picture
            :arg:   tweet is the information of one tweet, a json dictionary
        """
        tweet_saved_dict = {}
        tweet_saved_dict['id'] = tweet['id']
        tweet_saved_dict['text'] = tweet['full_text']
        tweet_saved_dict['media_url'] = tweet['extended_entities']['media'][0]['media_url_https']
        try:
            if self._download_picture(tweet_saved_dict['media_url'], tweet_saved_dict['id'], self.picture_dir):
                with self.lock:
                    with open(self.tweets_with_picture_file, 'a', encoding='utf8') as f:
                        json.dump(tweet_saved_dict, f, ensure_ascii=False)
                        f.write('\n')
                self.tweet_refined_count += 1
                self.finished_threads += 1
                self.working_threads -= 1
            else:
                with open(self.picture_downloaded_error_file, 'a', encoding='utf8') as ef:
                    json.dump(tweet_saved_dict, ef, ensure_ascii=False)
                    ef.write('\n')
        except Exception as e:
            self.log_info("Some error: %s" % str(e))

    def _refine_results(self):
        """ func:   Extract all tweets having at least one picture, save their full_text and download pictures"""
        self.log_info("Start extracting tweets having at least one picture...")
        refined_tweets = []
        if not os.path.isfile(self.all_result_file):
            self.log_info("No such a file: %s" % self.all_result_file)
            return
        with open(self.all_result_file, 'r', encoding='utf8') as f:
            for line in f.readlines():
                tweet_dict = json.loads(line.rstrip())
                try:
                    if tweet_dict['full_text']:
                        if tweet_dict['extended_entities']['media'][0]['media_url_https']:
                            refined_tweets.append(tweet_dict)
                except:
                    pass
        total_tweets = len(refined_tweets)
        for tweet in refined_tweets:
            if self.working_threads < self.MAX_THREADS:
                t = threading.Thread(target=self._save_one_refined_tweet, args=(tweet, ))
                t.start()
                self.working_threads += 1
                self.log_info("Working threads: {:<2d} | Maximum threads: {:<2d} "
                              "| Finished tweets: {:<5d} | Total tweets: {:<5d}".format(
                              self.working_threads, self.MAX_THREADS, self.finished_threads, total_tweets))
            time.sleep(0.2)
        self.log_info("Successfully refined and saved %d tweets" % self.tweet_refined_count)

    def log_info(self, string):
        t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        string = t + "\t" + string
        with open(self.log_path, 'a', encoding='utf8') as f:
            f.write(string + '\n')
        print(string)

    def run(self):
        max_tweet_id = -1
        self.log_info("Search key words: %s | Max searched tweets: %d" % (self.QUERY, self.MAX_TWEETS))
        if self.since_id:
            self.log_info("Start updating tweets since id: {:}...".format(self.since_id))
        else:
            self.log_info("Start downloading tweets...")
        while self.tweet_downloaded_count < self.MAX_TWEETS:
            try:
                if max_tweet_id <= 0:
                    if not self.since_id:
                        new_tweets = self.api.search(q=self.QUERY,
                                                     tweet_mode='extended',
                                                     count=self.COUNT_PER_QUERY,
                                                     )
                    else:
                        new_tweets = self.api.search(q=self.QUERY,
                                                     tweet_mode='extended',
                                                     count=self.COUNT_PER_QUERY,
                                                     since_id=self.since_id,
                                                     )
                else:
                    if not self.since_id:
                        new_tweets = self.api.search(q=self.QUERY,
                                                     tweet_mode='extended',
                                                     count=self.COUNT_PER_QUERY,
                                                     max_id=str(max_tweet_id - 1),
                                                     )
                    else:
                        new_tweets = self.api.search(q=self.QUERY,
                                                     tweet_mode='extended',
                                                     count=self.COUNT_PER_QUERY,
                                                     since_id=self.since_id,
                                                     max_id=str(max_tweet_id - 1),
                                                     )
                if not new_tweets:
                    self.log_info("No more tweets found!")
                    break
                self._save_all_result(new_tweets)
                max_tweet_id = new_tweets[-1].id
                earliest_tweet_time = new_tweets[-1].created_at
                self.log_info("earliest_tweet_time = %s" % earliest_tweet_time)
            except Exception as e:
                self.log_info("Some error: " + str(e))
                break
        self._refine_results()


if __name__ == '__main__':
    crawler = TwitterCrawler(clean_dir=True, since_id=None)
    crawler.run()
