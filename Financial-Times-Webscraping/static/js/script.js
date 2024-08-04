async function fetchNews() {
    const query = document.getElementById('search-query').value;
    const newsResults = document.getElementById('news-results');
    const fullArticle = document.getElementById('full-article');
    newsResults.innerHTML = 'Loading...';
    fullArticle.innerHTML = '';

    try {
        const response = await fetch(`/newsarticle?query=${query}`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (response.ok) {
            displayNews(data.results);
        } else {
            newsResults.innerHTML = 'No Posts found';
        }
    } catch (error) {
        newsResults.innerHTML = 'Error fetching news';
        console.error('Error:', error);
    }
}

function displayNews(articles) {
    const newsResults = document.getElementById('news-results');
    newsResults.innerHTML = '';

    articles.forEach(article => {
        const articleElement = document.createElement('div');
        articleElement.classList.add('news-item');

        articleElement.innerHTML = `
            <h2>${article.teaser_heading}</h2>
            <p>${article.teaser_category}</p>
            <p>${article.teaser_standfirst}</p>
            <p>${article.teaser_timestamp}</p>
            <img src="${article.teaser_image_src}" alt="Article Image">
            <button onclick="fetchFullArticle('${article.fullArticleLink}')">Read Full Article</button>
        `;

        newsResults.appendChild(articleElement);
    });
}

async function fetchFullArticle(link) {
    const fullArticle = document.getElementById('full-article');
    fullArticle.innerHTML = 'Loading...';

    try {
        const response = await fetch(`/fullArticle?link=${link}`, {
            method: 'GET'
        });
        const data = await response.json();
        
        if (response.ok) {
            displayFullArticle(data.fullArticle[0]);
        } else {
            fullArticle.innerHTML = 'Error fetching article';
        }
    } catch (error) {
        fullArticle.innerHTML = 'Error fetching article';
        console.error('Error:', error);
    }
}

function displayFullArticle(article) {
    const fullArticle = document.getElementById('full-article');
    fullArticle.innerHTML = '';

    fullArticle.innerHTML = `
        <h2>${article.fullArticleTitle}</h2>
        <p>${article.fullArticleSubText}</p>
        <img src="${article.fullArticleImage}" alt="Full Article Image">
        <p>${article.fullArticleImageCaption}</p>
        ${article.fullArticleContent.map(paragraph => `<p>${paragraph}</p>`).join('')}
    `;
}
