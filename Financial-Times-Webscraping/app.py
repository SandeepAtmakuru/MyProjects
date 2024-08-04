from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random
import time
import re

app = Flask(__name__)

ua = UserAgent()

class Headers:

    social_media_sites = [
        'https://www.facebook.com/',
        'https://www.twitter.com/',
        'https://www.linkedin.com/',
        'https://www.instagram.com/',
        'https://www.pinterest.com/',
        'https://www.reddit.com/',
        'https://www.tumblr.com/',
        'https://www.snapchat.com/',
        'https://www.tiktok.com/',
        'https://www.quora.com/'
    ]

    @staticmethod
    def smHeaders():
        return {
            'User-Agent': ua.random,
            'Referer': random.choice(Headers.social_media_sites),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        }

    @staticmethod
    def gabHeaders():
        return {
            'User-Agent': ua.random + '(compatible; AdsBot-Google-Mobile; +http://www.google.com/mobile/adsbot.html)',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.google.com/'
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/newsarticle', methods=["POST"])
def news_article():
    query = request.args.get("query")
    url = f"https://www.ft.com/search?q={query}&sort=relevance&expandRefinements=true&isFirstView=false"
    url2="https://www.ft.com/search?q={}&sort=date&isFirstView=true"
    time.sleep(2)
    response = requests.get(url=url, headers=Headers.gabHeaders())
    soup = BeautifulSoup(response.content, 'html.parser')
    article_list = soup.find('ul', class_="search-results__list")
    results_list = []
    if article_list:
        articles = article_list.find_all('div', class_="o-teaser o-teaser--article o-teaser--small o-teaser--has-image js-teaser".split())
        for article in articles:
            if article.find('div', class_="event-teaser__content-container"):
                continue
            teaser_heading = article.find('div', class_='o-teaser__heading')
            if teaser_heading:
                anchor_tag = teaser_heading.find('a')
                link = anchor_tag.get('href') if anchor_tag else None
                teaser_heading = teaser_heading.text
            else:
                link, teaser_heading = None, None
            teaser_category = article.find('a', class_='o-teaser__tag')
            teaser_category = teaser_category.text.strip() if teaser_category else None
            teaser_standfirst = article.find('p', class_='o-teaser__standfirst')
            teaser_standfirst = teaser_standfirst.text.strip() if teaser_standfirst else None
            teaser_timestamp = article.find('time', class_='o-teaser__timestamp-date')
            teaser_timestamp = teaser_timestamp['datetime'] if teaser_timestamp else None
            image = article.find('div', class_="o-teaser__image-placeholder")
            teaser_image_src = image.find('img', class_="o-teaser__image o-lazy-load".split())['data-src'] if image else None
            results_list.append({
                "fullArticleLink": link,
                "teaser_heading": teaser_heading,
                "teaser_category": teaser_category,
                "teaser_standfirst": teaser_standfirst,
                "teaser_timestamp": teaser_timestamp,
                "teaser_image_src": teaser_image_src
            })
        return jsonify({"results": results_list}), 200
    else:
        return jsonify({'results': "No Posts found"}), 400

@app.route('/fullArticle', methods=['GET'])
def get_full_article():
    link_addon = request.args.get('link')
    base_url = "https://www.ft.com"
    url = base_url + link_addon
    time.sleep(2)
    response = requests.get(url, headers=Headers.gabHeaders())
    if response.status_code != 200:
        return jsonify({'error': f"Failed to retrieve the page. Status code: {response.status_code}"}), 400
    soup = BeautifulSoup(response.content, 'html.parser')
    pattern = re.compile(r'/content/([a-f0-9\-]+)')
    match = pattern.search(url)
    if match:
        article_id = match.group(1)
    blogPost = soup.find('article', id='post-' + article_id)
    if blogPost:
        title_tag = blogPost.find('h2', class_="x-live-blog-post__title")
        blogArticleTitle = title_tag.text if title_tag else None
        body = blogPost.find('div', id='truncated-' + article_id)
        bodyContent = [p.text for p in body.find_all('p')] if body else []
        return jsonify({'blogPost': [{
            "blogArticleTitle": blogArticleTitle,
            "bodyContent": bodyContent
        }]})
    else:
        fullArticleTitle = soup.find('span', class_="headline__text").text
        fullArticleSubText = soup.find('div', class_="o-topper__standfirst").text
        mainImage = soup.find('figure', class_="n-content-image n-content-image--full")
        fullArticleImage = mainImage.find('img')["src"] if mainImage else None
        figueCaption = soup.find('figcaption', class_="n-content-picture__caption")
        fullArticleImageCaption = figueCaption.find('span').text if figueCaption else None
        full_article = soup.find('article', class_="n-content-body js-article__content-body".split())
        fullArticleContent = [p.text for p in full_article.find_all('p')] if full_article else []
        return jsonify({"fullArticle": [{
            "fullArticleTitle": fullArticleTitle,
            "fullArticleSubText": fullArticleSubText,
            "fullArticleImage": fullArticleImage,
            "fullArticleImageCaption": fullArticleImageCaption,
            "fullArticleContent": fullArticleContent
        }]}), 200

if __name__ == '__main__':
    app.run()
