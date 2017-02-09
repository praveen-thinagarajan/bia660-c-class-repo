# BIA-660-C Assignment-2
# 2/9/2017
# Praveen Thinagarajan (Stevens Id: 10418777)

import datetime
import csv

from collections import OrderedDict
from math import sqrt

class DataFrame(object):
    @classmethod
    def from_csv(cls, file_path, delimiting_character=',', quote_character='"'):
        with open(file_path, 'rU') as infile:
            reader = csv.reader(infile, delimiter=delimiting_character, quotechar=quote_character)
            dataa = []
            # Modifying row 559 of data for removing separator in integer variable
            for index, row in enumerate(reader):
                if index == 559:
                    row[2] = row[2].replace(',', '')
                dataa.append(row)
            return cls(list_of_lists=dataa)

    # ******************Task-#3 ************************************************

    # Class method that returns type of a column of data
    @classmethod
    def get_type_of_column(self, column, col_list):
        # Checking if all items of the column are integers
        is_int = True
        for col in col_list:
            try:
                if isinstance(int(col), int) == False:
                    is_int = False
            except ValueError:
                is_int = False
        if is_int:
            return int
        else:
            # Checking if all items of the column are dates
            is_date = True
            # try:
            for col in col_list:
                if (isinstance(col, int)):
                    is_date = False
                else:
                    try:
                        if not (isinstance(datetime.datetime.strptime(col, '%m/%d/%y %H:%M'), datetime.datetime)):
                            is_date = False
                    except ValueError:
                        is_date = False

            if is_date:
                # Converting each entry into Datetime objects
                for index, entry in enumerate(col_list):
                    col_list[index] = datetime.datetime.strptime(entry, '%m/%d/%y %H:%M')
                return datetime
            else:
                raise TypeError('The values in the column are strings and this operation cannot be performed.')
        return None

    # Class method to return 'Min' value in a column
    @classmethod
    def min(self, column):
        col_list = [row[column] for row in df.data]
        col_type = self.get_type_of_column(column, col_list)
        if col_type == int or col_type == datetime:
            return min(col_list)
        else:
            return None

    # Class method to return 'Max' value in a column
    @classmethod
    def max(self, column):
        col_list = [row[column] for row in df.data]
        col_type = self.get_type_of_column(column, col_list)
        if (col_type == int or col_type == datetime):
            return max(col_list)
        else:
            return None

    # Class method to return 'Median' value of a column
    @classmethod
    def median(self, column):
        col_list = [row[column] for row in df.data]
        col_type = self.get_type_of_column(column, col_list)
        if (col_type == int or col_type == datetime):
            col_list = sorted(col_list)
            if (len(col_list) % 2 == 1):
                median = (len(col_list) + 1) / 2
                return col_list[median]
            else:
                median_1 = len(col_list) / 2
                median_2 = median_1 + 1
                return (col_list[median_1] + col_list[median_2]) / 2
        else:
            raise TypeError('The values in the column are strings and this operation cannot be performed.')

    # Class method to return 'Mean' value of a column
    @classmethod
    def mean(self, column):
        col_list = [row[column] for row in df.data]
        col_type = self.get_type_of_column(column, col_list)
        summ = 0
        if (col_type == int):
            for col in col_list:
                summ = summ + int(col)
            mean = summ / len(col_list)
            return mean
        else:
            raise TypeError('The values in the column are strings and this operation cannot be performed.')

    # Class method to return 'Sum' value of a column
    @classmethod
    def sum(self, column):
        col_list = [row[column] for row in df.data]
        col_type = self.get_type_of_column(column, col_list)
        summ = 0
        if col_type == int:
            for col in col_list:
                summ = summ + int(col)
            return summ
        else:
            raise TypeError('The values in the column are strings and this operation cannot be performed.')

    # Class method to return 'Standard Deviation' value of a column
    @classmethod
    def std(self, column):
        col_list = [row[column] for row in df.data]
        col_type = self.get_type_of_column(column, col_list)
        sum = 0
        if (col_type == int):
            for col in col_list:
                sum = sum + int(col)
            num_items = len(col_list)
            mean = sum / num_items
            differences = [int(x) - mean for x in col_list]
            sq_differences = 0
            for d in differences:
                lis = [d ** 2 for d in differences]
            for item in lis:
                sq_differences = sq_differences + item
            return sqrt(sq_differences / len(col_list))
        else:
            raise TypeError('The values in the column are strings and this operation cannot be performed.')
    # ******************End of Task-#3 **********************************************

    # ******************Task-#4 ************************************************
    # Class method to add rows into data
    @classmethod
    def add_rows(self, list_of_lists):
        length = len(df.data[0])
        for row in list_of_lists:
            if (len(row) == length):
                df.data.append(row)
            else:
                raise ValueError('The length of the row does not match to that of the existing data')
        df.data = [OrderedDict(zip(df.header, row)) for row in df.data]
    # ******************End of Task-#4 ************************************************

    # ******************Task-#5 ************************************************
    # Class method to add a column into data
    @classmethod
    def add_columns(self, list_of_values, col_name):
        length_rows_data = len(df.data)
        length_values = len(list_of_values)
        if (length_rows_data == length_values):
            for index, headername in enumerate(df.header):
                df.data[index][col_name] = list_of_values[index]
            df.header.append(col_name)
        else:
            raise ValueError('The length of the column does not match to that of the existing data')
    # ******************End of Task-#5 ************************************************

    def __init__(self, list_of_lists, header=True):
        # ******************Task-#2************************************************
        # Stripping any leading and trailing whitespaces from strings in the data
        for each_list in list_of_lists:
            for index, word in enumerate(each_list):
                each_list[index] = word.strip()

        # ******************End of Task-#2******************************************
        if header:
            # Assigning header
            self.header = list_of_lists[0]
            self.data = list_of_lists[1:]
        else:
            self.header = ['column' + str(index + 1) for index, column in enumerate(list_of_lists)]
            self.data = list_of_lists

        # ******************Task-#1************************************************
        # Ensuring uniqueness of header names
        is_unique = (all(list_of_lists[0].count(x) == 1 for x in list_of_lists[0]))
        if not is_unique:
            raise TypeError('Elements in the header are not unique!')
        # ******************End of Task-#1******************************************

        self.data = [OrderedDict(zip(self.header, row)) for row in self.data]

    def __getitem__(self, item):
        # this is for rows only
        if isinstance(item, (int, slice)):
            return self.data[item]

        # this is for columns only
        elif isinstance(item, (str, unicode)):
            return [row[item] for row in self.data]

        # this is for rows and columns
        elif isinstance(item, tuple):
            if isinstance(item[0], list) or isinstance(item[1], list):

                if isinstance(item[0], list):
                    rowz = [row for index, row in enumerate(self.data) if index in item[0]]
                else:
                    rowz = self.data[item[0]]

                if isinstance(item[1], list):
                    if all([isinstance(thing, int) for thing in item[1]]):
                        return [
                            [column_value for index, column_value in enumerate([value for value in row.itervalues()]) if
                             index in item[1]] for row in rowz]
                    elif all([isinstance(thing, (str, unicode)) for thing in item[1]]):
                        return [[row[column_name] for column_name in item[1]] for row in rowz]
                    else:
                        raise TypeError('What the hell is this?')

                else:
                    return [[value for value in row.itervalues()][item[1]] for row in rowz]
            else:
                if isinstance(item[1], (int, slice)):
                    return [[value for value in row.itervalues()][item[1]] for row in self.data[item[0]]]
                elif isinstance(item[1], (str, unicode)):
                    return [row[item[1]] for row in self.data[item[0]]]
                else:
                    raise TypeError('I don\'t know how to handle this...')

        # only for lists of column names
        elif isinstance(item, list):
            return [[row[column_name] for column_name in item] for row in self.data]

    def get_rows_where_column_has_value(self, column_name, value, index_only=False):
        if index_only:
            return [index for index, row_value in enumerate(self[column_name]) if row_value == value]
        else:
            return [row for row in self.data if row[column_name] == value]


infile = open('SalesJan2009.csv')
lines = infile.readlines()
lines = lines[0].split('\r')
data = [l.split(',') for l in lines]
things = lines[559].split('"')
data[559] = things[0].split(',')[:-1] + [things[1]] + things[-1].split(',')[1:]

df = DataFrame(list_of_lists=data)
# get the 5th row
fifth = df[4]
sliced = df[4:10]
# get item definition for df [row, column]

# get the third column
tupled = df[:, 2]
tupled_slices = df[0:5, :3]

tupled_bits = df[[1, 4], [1, 4]]

# adding header for data with no header
df = DataFrame(list_of_lists=data[1:], header=False)

# fetch columns by name
named = df['column1']
named_multi = df[['column1', 'column7']]

# fetch rows and (columns by name)
named_rows_and_columns = df[:5, 'column7']
named_rows_and_multi_columns = df[:5, ['column4', 'column7']]

# testing from_csv class method
df = DataFrame.from_csv('SalesJan2009.csv')

rows = df.get_rows_where_column_has_value('Payment_Type', 'Visa')
indices = df.get_rows_where_column_has_value('Payment_Type', 'Visa', index_only=True)

rows_way2 = df[indices, ['Product', 'Country']]

# Testing assignment code
# ****************************************************************
# Testing - Task#3
# Minimum for dates
minimum_1 = df.min('Transaction_date')
print minimum_1

# Minimum for int
minimum_2 = df.min('Price')
print minimum_2

# Minimum for Str
# minimum_3=df.min('Name')
# print minimum_3

# Maximum for dates
maximum_1 = df.max('Transaction_date')
print maximum_1

# Maximum for int
maximum_2 = df.max('Price')
print maximum_2

# Maximum for Str
# maximum_3=df.max('Name')
# print maximum_3

# Median for dates
median_1 = df.median('Transaction_date')
print median_1

# Median for int
median_2 = df.median('Price')
print median_2

# Median for str
# median_3=df.median('Name')
# print median_3

# Mean for dates
# mean_1=df.mean('Transaction_date')
# print mean_1

# Mean for int
mean_2 = df.mean('Price')
print mean_2

# Mean for str
# mean_3=df.mean('Name')
# print mean_3

# Sum for dates
# sum_1=df.sum('Transaction_date')
# print sum_1

# Sum for int
sum_2 = df.sum('Price')
print sum_2

# Sum for str
# sum_3=df.sum('Name')
# print sum_3

# SD for dates
# std_1=df.std('Transaction_date')
# print std_1

# SD for int
std_2 = df.std('Price')
print std_2

# SD for str
# std_3=df.std('Name')
# print std_3

# End of Testing - Task#3

# Testing - Task#4
new_l1 = ['1/5/09 4:10', 'Product1', '1200', 'Mastercard', 'Nicola', 'Roodepoort', 'Gauteng', 'South Africa',
          '1/5/09 2:33', '1/7/09 5:13', '-26.1666667', '27.8666667']
new_l2 = ['1/5/09 4:12', 'Product2', '1300', 'Mastercard', 'Nicola', 'Roodepoort', 'Gauteng', 'South Africa',
          '1/5/09 2:33', '1/7/09 5:13', '-26.1666667', '27.8666667']
lists = []
lists.append(new_l1)
lists.append(new_l2)
df.add_rows(lists)
print len(df.data)

# Testing - Task#5
new_c1 = range(1000)
print len(df.data[0])
df.add_columns(new_c1, 'Added')
print len(df.data[0])