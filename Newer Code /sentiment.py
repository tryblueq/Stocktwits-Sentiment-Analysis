import pandas as pd
import requests
import datetime as dt
import os.path
from sqlalchemy import create_engine
import config
# import time

# will need to make sure there is a blank 'sentiment.csv' in the same folder as this .py file
# before starting to run this

# need to pass through a list of all of the equities
# The below code takes the series of tickers and puts it into a list format we can pass into the function
# Change the below location based on location
stocks_df = pd.read_csv('/home/ubuntu/sentiment/sentiment_stocks.csv')
stocks = stocks_df['Stock'].tolist()

def ticker_sentiment(tickers):
    sentiment_list = []
    time = dt.datetime.today().strftime("%m/%d/%Y %H:%M")
    time = str(time)
    date = time.split()[0]
    hour = time.split()[1]
    print('Starting Scrape: ', time)
    for ticker in tickers:
        r = requests.get(f'https://stocktwits.com/symbol/{ticker}')
        text = r.text
        sentiment_word = text.find('sentimentChange')
        sentiment = text[sentiment_word + 17:sentiment_word + 23]
        comma = sentiment.find(',')

        if comma != -1:
            sentiment = sentiment[:comma]
            sentiment_list.append([ticker, date, hour, float(sentiment)])
        else:
            sentiment_list.append([ticker, date, hour, 0.0])
    return sentiment_list

def sentiment(stocks):
    stock_sentiments = ticker_sentiment(stocks)
    df_sentiment = pd.DataFrame(stock_sentiments, columns=['Stock', 'Date', 'Hour', 'Sentiment'])
    df_sentiment = df_sentiment.set_index('Stock')
    sql_commit(df_sentiment)

    return df_sentiment


def sql_commit(df):
    engine = create_engine("mysql+mysqlconnector://{user}:{pw}@{host}/{db}"
                           .format(user=config.user,
                                   pw=config.passwd,
                                   host=config.host,
                                   db=config.db_name))

    df.reset_index(inplace=True)

    df.to_sql('stock_sentiment', con=engine, if_exists='append', index=False)


print('Starting Script')
sentiment_df = sentiment(stocks)
time = dt.datetime.today().strftime("%m/%d/%Y %H:%M")
time = str(time)
print('Scrape Complete: ', time)





