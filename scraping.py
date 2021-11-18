#Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager

#import Pandas and datetime dependency
import pandas as pd
import datetime as dt

#Connect to mongo and establish communication between code and database
def scrape_all():
    #Initiate headless driver for deployment
    #Set executable path for Splinter
    executable_path = {'executable_path' : ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless = True)

    #Set news title and paragraph variables
    news_title, news_paragraph = mars_news(browser)

    #Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }

    #Stop webdriver and return data
    browser.quit()
    return data

#Create function for Mars News site
def mars_news(browser):
    #Scrape Mars News Site
    #Visit the Mars Nasa News Site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    #Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html,'html.parser')

    #Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')

        #Title and Summary text
        slide_elem.find('div', class_='content_title')

        #Use the parent element to find the first 'a' tag and save it as "new_title"
        news_title = slide_elem.find('div', class_='content_title').get_text()
        
        #Use the parent element to find the paragraph text
        news_paragraph = slide_elem.find('div', class_='article_teaser_body').get_text()
    
    except AttributeError:
        return None, None
    
    return news_title, news_paragraph

# ### JPL Space Featured Images

def featured_image(browser):
    #Visit the space images Site
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    #Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    #Parse the resulting html with soup
    html=browser.html
    img_soup = soup(html, 'html.parser')

    #Add try/except for error handling
    try:
        #find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None

    #Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url


# ## Mars Facts
def mars_facts():
    #Add try/except for error handling
    try:
        #Scrape table using pandas
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None

    #Assign columns and set index of dataframe    
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    #Convert df back to html-ready code, add bootstrap
    return df.to_html(classes="table table-striped")

#Very Important last line!  #End the automated browsing session
#browser.quit()
#Tell Flask the script is complete and ready for action
if __name__ == "__main__":
    #if running as script, print scraped data
    print (scrape_all())

