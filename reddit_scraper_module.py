"""This module contains helper functions for the PushShift API object.
   The functions in thiss module help a user taken in a PushShift API
   return object, clean the values, and return a dataframe with the
   cleaned values as well as date, and stock ticker values as separate
   rows.

   Returns:
   [Pandas DataFrame]: DataFrame object cleaned reddit submissions."""
import datetime as dt
import re

class RedditData:
    '''
    This class contains helper functions that parse through a PushShift API object to return a
    cleaned dataframe with separated Date-wise Tags and Comment values.
    '''
    def __init__(self, name):
        self.name = name
    @staticmethod

    def has_numbers(input_string):
        '''
        This function looks at the $Tag and checks if it contains a dollar value or a ticker symbol.
        For eg. is it $9 or $AMC. Returns True if it is a number and false if it is a string.
        '''
        return any(char.isdigit() for char in input_string)

    @staticmethod
    def get_subreddit_column(subreddit, lst_tags):
        '''
        This function takes the channel variable and the dataframe of api results as input
        and adds a column in the same dataframe of the length of the dataframe and populates
        it with the name of the subreddit (channel variable) name.
        '''
        arr_subreddit = []
        size = len(lst_tags)
        arr_subreddit += size * [str(subreddit)]
        return arr_subreddit

    @staticmethod
    def cashtags(submissions):
        '''
        This function takes the api JSON values and the dataframe. It extracts the $Tags from the
        comments and stores them in a separate column, corresponding to the row of the comment.
        It also filters out the $Tags that are empty and those that have a $Numerical value.
        Returns a list of tags and a list of comments.
        '''
        #pylint: disable=too-many-locals
        tag_list = []
        comment_list = []
        date_list = []
        subreddit_list = []
        lst_tag = []
        lst_comments = []
        lst_date = []
        lst_subreddit = []
        for submit in submissions:
            words = submit.title.split()
            cashtags = list(set(filter(lambda word: word.lower().startswith('$'), words)))
            if  len(cashtags) > 0:
                val = RedditData.has_numbers(str(cashtags))
                if  not val:
                    tag_list.append(cashtags)
                    comment_list.append(submit.title)
                    date = dt.datetime.fromtimestamp(submit.created_utc)
                    #pylint: disable=syntax-error
                    date = date.replace(tzinfo=dt.timezone.utc).strftime("%m/%d/%Y %H")
                    date_list.append(date)
                    subreddit_list.append(submit.subreddit)
        length = len(tag_list)
        for i in range(length):
            if len(tag_list[i]) >= 1:
                for j in range(len(tag_list[i])):
                    clean_tag = RedditData.has_special_chars((tag_list[i][j]))
                    lst_tag.append(clean_tag)
                    lst_comments.append(comment_list[i])
                    lst_date.append(date_list[i])
                    lst_subreddit.append(subreddit_list[i])
        return lst_tag, lst_comments, lst_date, lst_subreddit

    @staticmethod
    def add_to_df(tag_values, comment_values, date_values, subreddit_values, df_data):
        '''
        This function takes the list of tags, list of columns, subreddit list and the working
        dataframe as inputs and appends each values to the corresponding rows.
        '''
        length_comment = len(comment_values)
        for i in range(length_comment):
            df_length = len(df_data)
            df_data.loc[df_length] = date_values[i], comment_values[i], tag_values[i], subreddit_values[i]

    @staticmethod
    def has_special_chars(input_string):
        '''
        This function takes a string that is stripped of the $ sign from the ticker and
        returns coded value. Codes:- 1: Valid Ticker (No special characters), -1:
        Trailing Special Character(Requires removal of trailing character) and 0:
        Invalid Ticker (Contains non-trailing special characters).
        '''
        sub_str = input_string[1:]
        dollar_char = input_string[:1]
        bool_result = RedditData.__have_special_chars(sub_str)
        if bool_result:
            sub_str = re.sub(r'\W+', '', sub_str)
        clean_string = dollar_char + sub_str
        return clean_string.upper()
    #pylint: disable=inconsistent-return-statements
    @staticmethod
    def __have_special_chars(sub_string):
        '''
        This is a helper function used inside the has_special_chars() function that takes
        in a string as an input and returns boolean True if the passed string contains a
        special character.
        '''
        regexp = re.compile('[^a-zA-Z]+')
        if regexp.search(sub_string):
            return True
