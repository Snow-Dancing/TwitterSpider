# twitter spider

## 使用twitter的官方API-tweepy从twitter上爬取带有某关键词的tweet文本和图片数据 

## 运行环境:
1. Python3

2. 安装了requests, tweepy库

3. 可以科学上网

## 使用方法:
1. 打开crawler.py，根据自己的代理情况修改self.proxy和self.QUERY的值

2. 设置搜索关键词：self.QUERY

3. 倒数第二行，clean_dir代表初始会清除temp_data和picture文件夹，即删除历史记录，慎用

4. 倒数第二行，since_id代表查找比这个id更大的tweet，也就是最新的tweet，用于更新使用

5. 若是非更新状态，since_id设置为None，没有时间限制，爬虫会爬取限制时间内(当前十几天左右)能爬到的所有tweet

6. 爬虫爬取顺序是从最新发布的tweet到之前发布的tweet

7. 若是更新状态，把since_id设置成上一次爬取最大的id号就行，
   一般是all_result.json或者updating_all_result.json的第一行，
   爬虫会爬取比这个id更大的tweet，也就是上次爬取之后更新的twitter

8. 打开id_collection.py设置tweepy账号、开发者权限等四个信息。

9. 以上设置完成后，python3 直接运行crawler.py

## 文件夹介绍:
1. tem_data文件夹保存所有的搜索结果的文本文件

2. picture文件夹保存所有下载的图片文件

3. tem_data/all_result.json文件保存所有的搜索结果，无论有没有图片，一行一个tweet，json格式，存储所有键值对

4. tem_data/tweets_with_picture.json文件保存具有图片的tweet，一行一个tweet，json格式，只存储id，full_text和图片链接

5. tem_data/updating_all_result.json文件保存更新时所有的搜索结果，用来和非更新的结果区分开

6. tem_data/picture_download_error_tweets.json文件保存有图片链接但是下载图片出错的tweet，不计入最终保存的数据库。

7. picture/ 文件夹下图片的命名格式是：图片对应tweet的id + 图片格式
