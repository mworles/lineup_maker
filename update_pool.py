from nf_scraper import scrape


url = 'https://www.numberfire.com/nfl/fantasy/fantasy-football-projections'
urls = [url, url + '/d']

scrape(urls)
#import filter_players
#import assign_id
