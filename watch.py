from scrape import merge_domain
from time import sleep
from tqdm import tqdm
if __name__ == '__main__':
    domains = [
        "http://Cnn.com",
        "http://Nytimes.com",
        "http://Theguardian.com",
        "http://Bbc.co.uk/news/",
        "http://Washingtonpost.com",
        "http://Huffingtonpost.com",
        "http://Indiatimes.com",
        "http://News.yahoo.com",
        "http://Weather.com",
        "http://Forbes.com",
        "http://Foxnews.com",
        "http://Shutterstock.com",
        "http://Accuweather.com",
        "http://Bloomberg.com",
        "http://Timesofindia.indiatimes.com",
        "http://Reuters.com",
        "http://Wsj.com",
        "http://Usatoday.com",
        "http://Money.cnn.com",
        "http://Wunderground.com",
        "http://Cnbc.com",
        "http://Drudgereport.com",
        "http://Chron.com",
        "http://Nbcnews.com",
        "http://Time.com",
        "http://Latimes.com",
        "http://Chinadaily.com.cn",
        "http://Usnews.com",
        "http://Economictimes.indiatimes.com",
        "http://Nypost.com",
        "http://Theatlantic.com",
        "http://Indianexpress.com",
        "http://Cbsnews.com",
        "http://News.com.au",
        "http://Thehill.com",
        "http://Hindustantimes.com",
        "http://Abcnews.go.com",
        "http://Sfgate.com",
        "http://Nationalgeographic.com",
        "http://Thehindu.com",
        "http://Cbc.ca/news/",
        "http://Dw.com",
        "http://Weather.gov",
        "http://Thedailybeast.com",
        "http://Hollywoodreporter.com",
        "http://Smh.com.au",
        "http://Economist.com",
        "http://Topix.com",
    ]
    while True:
        for ind, domain in enumerate(domains):
            print 'Domain ', ind, ' - ', domain
            merge_domain(domain)
        print 'Sleeping for one half hour'
        sleep(1800)
