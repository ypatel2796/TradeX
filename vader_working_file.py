"""[This module contains helper functions for generating the vader sentiment scores
    for the reddit api submissions.]

Returns:
    [DataFrame]: [A pandas DataFrame containing the dates and corresponding
     weighted sentiment scores.]
"""
#pylint: disable=wrong-import-position
import pandas as pd
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

VAR = 0.5

#df_working = pd.read_csv('Reddit_Test.csv')
sia = SentimentIntensityAnalyzer()
class VaderReddit():
    """[This class contains helper functions to compute sentiment scores for each reddit submission
        using VADER.]
    """
    def __init__(self) -> None:
        pass
    @staticmethod
    def add_vader_scores(df_rd):
        """[This function accepts a dataframe of reddit submissions
            and applies vader sentiment scores to the comments column.]

        Args:
            df_rd ([DataFrame]): [This is the dataframe of fetched and cleaned reddit submissions]
        """
        df_rd['Negative'] = df_rd['Comment'].apply(lambda x:sia.polarity_scores(str(x))['neg'])
        df_rd['Neutral'] = df_rd['Comment'].apply(lambda x:sia.polarity_scores(str(x))['neu'])
        df_rd['Positive'] = df_rd['Comment'].apply(lambda x:sia.polarity_scores(str(x))['pos'])
        df_rd['Compound'] = df_rd['Comment'].apply(lambda x:sia.polarity_scores(str(x))['compound'])

    @staticmethod
    def add_vader_weighted_sentiments(df_working):
        """[This function takes the dataframe with vader scores and adds weighted sentiment
            scores as columns]

        Args:
            df_working ([DataFrame]): [DataFrame with appended vader sentiment scores]
        """
        df_working['Weighted_Sentiment_Neg'] = df_working.apply(lambda row: (row['Negative']
                                                                             *row['Compound']
                                                                if row['Compound'] > 0 or
                                                                row['Compound'] < 0
                                                                else row['Negative'] *
                                                                VAR), axis=1)
        df_working['Weighted_Sentiment_Neu'] = df_working.apply(lambda row:(row['Neutral']
                                                                            *row['Compound']
                                                                if row['Compound'] > 0 or
                                                                row['Compound'] < 0
                                                                else row['Neutral'] *
                                                                VAR), axis=1)
        df_working['Weighted_Sentiment_Pos'] = df_working.apply(lambda row:(row['Positive']
                                                                             *row['Compound']
                                                                if row['Compound'] > 0 or
                                                                row['Compound'] < 0
                                                                else row['Positive'] *
                                                                VAR), axis=1)

        df_working['Sum_Weights'] = df_working.apply(lambda row:(row['Weighted_Sentiment_Neg'] +
                                                                row['Weighted_Sentiment_Neu'] +
                                                                row['Weighted_Sentiment_Pos']),
                                                            axis=1)

    @staticmethod
    def get_subset(stock_name, df_working_main):
        """[This function subsets the inputted dataframe based on the search query
        (ticker symbol) and returns the resulting subset dataframe]

        Args:
            stock_name ([String]): [Stock Ticker Symbol: $AMC]
            df_working_main ([DataFrame]): [DataFrame of reddit submissions,
                              sentiment scores, and weighted_sentiment_scores]

        Returns:
            [DataFrame]: [Resulting dataframe subset based on search query of stock name.]
        """
        if len(df_working_main) != 0:
            df_working_sub = df_working_main.loc[(df_working_main['Tags'] == stock_name)]
        return df_working_sub.sort_values(by='Date')

    @staticmethod
    def get_score(df_working_sub):
        """[This function groups the rows by date and aggregates the scores into sum and count.
            Creates another column 'Sentiment_Score' with sum of sentiment scores/count.]

        Args:
            df_working_sub ([DataFrame]): [Subset DataFrame based on search query]

        Returns:
            [DataFrame]: [DataFrame of Dates and Scores for each data for visualization.]
        """
        df_working_grp = df_working_sub.groupby('Date')['Sum_Weights'].aggregate(['sum','count'])
        df_working_grp['Sentiment_Score'] = df_working_grp.apply(lambda x: (x['sum'] /
                                                                        x['count']), axis=1)
        return pd.DataFrame(df_working_grp)
