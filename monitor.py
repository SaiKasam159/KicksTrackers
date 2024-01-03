import requests
import json
import time
from fp.fp import FreeProxy

# Lists to keep track of which products have been recorded
jordans_instock = []
nike_instock = []
snkrs_instock = []

# Webhooks for each of the channels in my custom Discord Server 
jordans_channel_webhook = 'https://discord.com/api/webhooks/1189636969161040073/FagVl-yrnHjKml13RrEq_xcsXrvhNnrpbG4AfbSLDQu51Mf3RnxwKfgNRiVDEXGzaRfS'
nike_channel_webhook = 'https://discord.com/api/webhooks/1189942534517051512/iGUWnhTRQRNZSleCldyubvn-tFxCEGOwACBYmS1_R8OUf3B8qeqXUiRE8gVzsbt--Lgs'
snkrs_channel_webhook = 'https://discord.com/api/webhooks/1191019888966381698/n7wO50NhtL170-IzY-RgxQwrpHJN0fXhwp8pzLR5YWh2-0Iye8msspecVQAsygVRQ4DR'
testing_webhook = 'https://discord.com/api/webhooks/1189962255274610720/69gMnTcyLojjSNDw1PsYbK4-_j4eYUo3EewkykbCOqLWBUjfnZAUxHFys0RXqJmnQWnY'

# The APIs from which the data is being fetched
air_jordans_api_target_url = 'https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=5BFC52F66E37C95FCB641DBC401EB101&country=gb&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(GB)%26filter%3Dlanguage(en-GB)%26filter%3DemployeePrice(true)%26filter%3DattributeIds(0f64ecc7-d624-4e91-b171-b83a03dd8550%2C16633190-45e5-4830-a068-232ac7aea82c%2C193af413-39b0-4d7e-ae34-558821381d3f%2C498ac76f-4c2c-4b55-bbdc-dd37011887b1)%26anchor%3D24%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D24&language=en-GB&localizedRangeStr=%7BlowestPrice%7D%E2%80%94%7BhighestPrice%7D'
nike_api_target_url = 'https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=5BFC52F66E37C95FCB641DBC401EB101&country=gb&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(GB)%26filter%3Dlanguage(en-GB)%26filter%3DemployeePrice(true)%26filter%3DattributeIds(0f64ecc7-d624-4e91-b171-b83a03dd8550%2C16633190-45e5-4830-a068-232ac7aea82c%2C193af413-39b0-4d7e-ae34-558821381d3f)%26anchor%3D24%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D24&language=en-GB&localizedRangeStr=%7BlowestPrice%7D%E2%80%94%7BhighestPrice%7D'
snkrs_api_target_url = 'https://api.nike.com/product_feed/threads/v3/?anchor=50&count=50&filter=marketplace%28GB%29&filter=language%28en-GB%29&filter=inStock%28true%29&filter=productInfo.merchPrice.discounted%28false%29&filter=channelId%28010794e5-35fe-4e32-aaff-cd2c74f89d61%29&filter=exclusiveAccess%28true%2Cfalse%29'

# Proxy Server and Headers for anonymous web scraping
proxy_obj = FreeProxy(country_id='GB', rand=True)
proxy = {'http': proxy_obj.get()}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}

# Sends message to Discord Server
def discord_webhook(webhook, title, full_price, current_price, colour, image, discounted, bestseller):
    data = {
        'embeds': [{
            'title': title,
            'thumbnail': {'url': image},
            'footer': {'text': 'Developed by Sai K Kasam'},
            'fields': [
                {'name': 'Full Price', 'value': str(full_price)},
                {'name': 'Current Price', 'value': str(current_price)},
                {'name': 'Colour', 'value': colour},
                {'name': 'Is Discounted?', 'value': discounted},
                {'name': 'Is BestSeller', 'value': bestseller},
            ]
        }]
    }

    result = requests.post(webhook, data = json.dumps(data), headers={'Content-type': 'application/json'})
    print(f'{result.status_code} : {requests.status_codes._codes[result.status_code][0]}')

# Scrapes the target API using the requests module and returns JSON output
def scrape_site(target_url, site):

    html = requests.get(url=target_url, timeout=20, verify=True, headers=headers, proxies=proxy)
    output = json.loads(html.text)

    if site == 'nike':
        return output['data']['products']['products']
    
    elif site == 'snkrs':
        return output['objects']

# Compares the shoes scraped to see if I already have them stored in the lists above
def comparison(instock_list, item, webhook, site, start):
    
    try:
        id = item['id']
        availability = item['inStock']
    except:
        id = item['productInfo'][0]['productContent']['fullTitle']
        availability = item['productInfo'][0]['availability']['available']

    if (id in instock_list) and (availability == False):
            instock_list.remove(id)

    if (id not in instock_list) and (availability == True):
            instock_list.append(id)

    # Sends the message with all the information about the shoe to my Discord Server
    if start == 0:
        if site == 'nike':
            discord_webhook(
                webhook = webhook,
                title = item['title'],
                full_price= item['price']['fullPrice'],
                current_price= item['price']['currentPrice'],
                colour = item['colorDescription'],
                image = item['images']['portraitURL'],
                discounted = item['price']['discounted'],
                bestseller= item['isBestSeller'],
            )

        elif site == 'snkrs':
            # Sometimes the SNKRS website doesn't include photos so I had to use a try and except block
            try:
                discord_webhook(
                    webhook = webhook,
                    title = item['productInfo'][0]['productContent']['fullTitle'],
                    full_price= item['productInfo'][0]['merchPrice']['fullPrice'],
                    current_price= item['productInfo'][0]['merchPrice']['currentPrice'],
                    colour = item['productInfo'][0]['productContent']['colorDescription'],
                    image = item['publishedContent']['nodes'][0]['nodes'][0]['properties']['squarishURL'],
                    discounted = item['productInfo'][0]['merchPrice']['discounted'],
                    bestseller= 'NOT APPLICABLE',
                )
            except:
                print("Some of the data couldn't be fetched")

# Filters shoes based on certain parameters 
def shoe_filter(product, discounted, bestseller, wanted_phrases, unwanted_phrases, gender, max_price, site):
    
    result = True

    try:
        title = product['title']
        price = product['price']['currentPrice']
        is_prod_discounted = product['price']['discounted']   
    except:
        title = product['productInfo'][0]['productContent']['fullTitle']
        price = product['productInfo'][0]['merchPrice']['currentPrice']
        is_prod_discounted = product['productInfo'][0]['merchPrice']['discounted']

    if not (any(phrase in title for phrase in wanted_phrases)):
        result = False
      
    if any(phrase in title for phrase in unwanted_phrases):
        result = False
        
    if discounted:
        if (is_prod_discounted == False):
            result = False

    if bestseller:
        if (product['isBestSeller'] == False):
            result = False

    # Nike API only has Men's Shoes so won't need to filter for Men
    if gender == 'male' and site == 'snkrs':
        if ('WOMEN' in product['productInfo'][0]['merchProduct']['genders'][0]):
            result = False

    if (price > max_price):
            result = False
        
    return result

start = 1
while True:

    # Fetches products and stores them in their respective lists
    jordan_products = scrape_site(target_url=air_jordans_api_target_url, site='nike')
    nike_products = scrape_site(target_url=nike_api_target_url, site='nike')
    snkrs_products = scrape_site(target_url=snkrs_api_target_url, site='snkrs')
    
    for product in jordan_products:
        if shoe_filter(product, discounted= True, bestseller= False, wanted_phrases=['Air Jordan'], unwanted_phrases=['FlyEase'], gender= 'male', max_price=100, site= 'nike'):
            comparison(jordans_instock, product, jordans_channel_webhook, 'nike', start)

    for product in nike_products:
        if shoe_filter(product, discounted= True, bestseller= False, wanted_phrases=['Dunk', 'Force', 'Retro'], unwanted_phrases=[], gender= 'male', max_price=200, site= 'nike'):
            comparison(nike_instock, product, nike_channel_webhook, 'nike', start)
        
    for product in snkrs_products:
        if shoe_filter(product, discounted= False, bestseller= False, wanted_phrases=[''], unwanted_phrases=[], gender= 'male', max_price=500, site= 'snkrs'):
            comparison(snkrs_instock, product, snkrs_channel_webhook, 'snkrs', start)
        
    # Sends messages every 10 mintues
    start = 0
    time.sleep(600)