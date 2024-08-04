from bs4 import BeautifulSoup
import requests
import pandas as pd


def price_range(r):
        if not isinstance(r, int):
            raise ValueError('Enter correct value for price range')
        
        url=f'https://www.flipkart.com/search?q=mobiles%20under%20{r}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off'
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}
        r=requests.get(url,headers).content
        soup=BeautifulSoup(r,'html.parser')
        return soup
def get_data(soup):
    Data = pd.DataFrame(columns=['Mobile', 'Rating', 'Specs','Price','Link'])
    divs = soup.find_all('div', class_="_2kHMtA")
    for item in divs:
        if(item.find('div',class_='_2tfzpE')):
            continue
        mobile_name = item.find('div', class_='_4rR01T')
        if mobile_name:
            mobile_name = mobile_name.text
        else:
            mobile_name = ''
        
        rating = item.find('div', {'class': '_3LWZlK'})
        if rating:
            rating = rating.text
        else:
            rating = ''
        
        specs = item.find('div', class_="fMghEO")
        if specs:
            specs = specs.text
        else:
            specs = ''
        
        price = item.find('div', class_='_30jeq3 _1_WHN1')
        if price:
            price = price.text
        else:
            price = '' 
        link=item.find('a')
        link=link['href']
        link='https://www.flipkart.com'+link
        Data.loc[len(Data)]=[mobile_name, rating, specs,price,link]
    return Data

r=int(input("Enter the price range--->"))
p=price_range(r)
d=get_data(p)
print(d)
d.to_csv('Mobile_data4.csv', mode='a',header=False, index=False)