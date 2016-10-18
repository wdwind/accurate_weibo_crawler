accurate_weibo_crawler
===================

A crawler originally designed for detecting weibo deletion. One can use it to accurately track a few weibo users, i.e., detecting weibo creation/deletion, outputting all weibos sent by a user to a csv file, and capturing screenshots of weibos as well as hot comments. Note that this crawler is "accurate", which means it is not intended to be used to crawl huge amount of weibos aimlessly.

## Features
- [x] Crawl weibos of some users
- [x] Check if the user post some weibos
- [x] Check if the user delete some weibos
- [x] Capture screenshots of weibos
- [x] Capture screenshots of the hot comments of weibos
- [x] Export weibos as csv format
- [x] Export deleted weibos as csv format
- [ ] Crawl users' comments
- [ ] Instagram support
- [ ] Twitter support
- [ ] Echo support

## Installation

 1. Install requirements
   - [Python 2.7.x](http://docs.python-guide.org/en/latest/starting/installation/)
   - [pip](https://pip.pypa.io/en/stable/installing/)
   - [git](https://git-scm.com/)
   - [PhantomJS](http://phantomjs.org/download.html)
   - [virtualenv](https://virtualenv.pypa.io/en/stable/installation/) (Recommended)
 2. Clone the git: `git clone https://github.com/wdwind/accurate_weibo_crawler`
 3. Go into the new directory: `cd accurate_weibo_crawler`
 4. (Optional) Create a virtual environment: `virtualenv .env`
 5. (Optional) Activate the virtual environment: `.env\scripts\activate`
 6. Install dependencies: `pip install -r requirements.txt`

## Configuration
Copy file `config.json.example` and rename it as `config.json`. All configuration options are in `config.json`.

 - `mode`: The mode of the crawler.
  1. `normal`: Crawl weibo once; capture screenshots once.
  2. `weibo`: Only crawl weibo once.
  3. `screenshot`: Only capture screenshots once.
  4. `loop`: Loop the normal mode every 5 minutes.
  5. `export`: Export all crawled weibo to csv file(s).
 - `db`: Database. Let the default value here except if you want to use multiple databases.
 - `phantomjs`: The path to the executable PhantomJS binary, e.g., `C:\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe`.
 - `timeout`: Timeout when capturing the screenshots (in milliseconds). This value should be set based on your Internet connection speed.
 - `access_token` and `expires_in`. Go to the following link:

    https://open.weibo.cn/oauth2/authorize?client_id=211160679&response_type=token&redirect_uri=http://oauth.weico.cc&key_hash=1e6e33db08f9192306c4afa0a61ad56c&packagename=com.eico.weico&display=mobile&scope=email,direct_messages_read,direct_messages_write,friendships_groups_read,friendships_groups_write,statuses_to_me_read,follow_app_official_microblog,invitation_write
    
    Finish the authorization. And then you will be redirected to a blank page where you can get the `access_token` and `expires_in` from the url:
    
    http:// oauth.weico.cc/#access_token=**【This is your `access_token`】**&remind_in=xxx&expires_in=**【This is your `expires_in`】**&refresh_token=xxx&uid=xxx&scope=xxx. 
 - `task`: The specific accounts and tasks you would like the crawler to perform.
    - `uid`: Id of the user to be crawled. This id is contained in the url of a user's homepage.
    - `name`: User's name. You can input anything here.
    - `screenshots_path`: The path to store the screenshots.
    - `temp_screenshots_path`: The path to store the temporary screenshots. Because the quality of the screenshot highly depends on the network connectivity, sometimes the screenshots are just nothing. This folder let you check the quality of screenshots manually, and move the good ones into `screenshots_path`.
    - `screenshots`: Set whether to capture the screenshots of weibo.
    - `screenshots_hot_comments`: Set whether to capture the screenshots of the hot comments.

## Usage

`python crawler.py`

## Disclaimer
Since Weibo's (public or private) APIs are extremely unstable, there is no guarantee that the program will give the right output. Use it at your own risk.