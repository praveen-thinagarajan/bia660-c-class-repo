# BIA-660-C Assignment-3
# 2/17/2017
# Praveen Thinagarajan (Stevens Id: 10418777)

import datetime
import csv
import collections

from collections import OrderedDict
from math import sqrt
from collections import defaultdict



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

    # Class method that returns type of a column of data
    @classmethod
    def get_type_of_column(cls, col_list,is_operation):
        # Checking if all items of the column are integers
        is_int = True
        for col in col_list:
            try:
                if not isinstance(int(col), int):
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
                if isinstance(col, int):
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
                if is_operation:
                    raise TypeError('The values in the column are strings and this operation cannot be performed.')
                else:
                    return str

    # Instance method to return 'Min' value in a column
    def min(self, column):
        col_list = [row[column] for row in self.data]
        col_type = DataFrame.get_type_of_column(col_list,True)
        if col_type == int or col_type == datetime:
            return min(col_list)
        else:
            return None

    # Instance method to return 'Max' value in a column
    def max(self, column):
        col_list = [row[column] for row in self.data]
        col_type = DataFrame.get_type_of_column(col_list,True)
        if col_type == int or col_type == datetime:
            return max(col_list)
        else:
            return None

    # Instance method to return 'Median' value of a column
    def median(self, column):
        col_list = [row[column] for row in self.data]
        col_type = DataFrame.get_type_of_column(col_list,True)
        if col_type == int or col_type == datetime:
            col_list = sorted(col_list)
            if len(col_list) % 2 == 1:
                median = (len(col_list) + 1) / 2
                return col_list[median]
            else:
                median_1 = len(col_list) / 2
                return col_list[median_1/2]
        else:
            raise TypeError('The values in the column are strings and this operation cannot be performed.')

    # Instance method to return 'Mean' value of a column
    def mean(self, column):
        col_list = [row[column] for row in self.data]
        col_type = DataFrame.get_type_of_column(col_list,True)
        summ = 0
        if col_type == int:
            for col in col_list:
                summ += int(col)
            mean = summ / len(col_list)
            return mean
        else:
            raise TypeError('The values in the column are strings and this operation cannot be performed.')

    # Instance method to return 'Sum' value of a column
    def sum(self, column):
        col_list = [row[column] for row in self.data]
        col_type = DataFrame.get_type_of_column(col_list,True)
        summ = 0
        if col_type == int:
            for col in col_list:
                summ = summ + int(col)
            return summ
        else:
            raise TypeError('The values in the column are strings and this operation cannot be performed.')

    # Instance method to return 'Standard Deviation' value of a column
    def std(self, column):
        col_list = [row[column] for row in self.data]
        col_type = DataFrame.get_type_of_column(col_list,True)
        sum = 0
        if col_type == int:
            for col in col_list:
                sum += int(col)
            num_items = len(col_list)
            mean = sum / num_items
            differences = [int(x) - mean for x in col_list]
            sq_differences = 0
            for d in differences:
                lis = [d ** 2 for d in differences]
            for item in lis:
                sq_differences += item
            return sqrt(sq_differences / len(col_list))
        else:
            raise TypeError('The values in the column are strings and this operation cannot be performed.')


    # Instance method to add rows into data
    def add_rows(self, list_of_lists):
        length = len(self.data[0])
        for row in list_of_lists:
            if len(row) == length:
                self.data.append(row)
            else:
                raise ValueError('The length of the row does not match to that of the existing data')
        self.data = [OrderedDict(zip(self.header, row)) for row in self.data]


    # Instance method to add a column into data
    def add_columns(self, list_of_values, col_name):
        length_rows_data = len(self.data)
        length_values = len(list_of_values)
        if length_rows_data == length_values:
            for index, header_name in enumerate(self.header):
                self.data[index][col_name] = list_of_values[index]
            self.header.append(col_name)
        else:
            raise ValueError('The length of the column does not match to that of the existing data')

    def __init__(self, list_of_lists, header=True):
        # Stripping any leading and trailing whitespaces from strings in the data

            for each_list in list_of_lists:
                for index, word in enumerate(each_list):
                    each_list[index] = str(word).strip()

            if header:
                # Assigning header
                self.header = list_of_lists[0]
                self.data = list_of_lists[1:]
            else:
                self.header = ['column' + str(index + 1) for index, column in enumerate(list_of_lists)]
                self.data = list_of_lists

            # Ensuring uniqueness of header names
            is_unique = (all(list_of_lists[0].count(x) == 1 for x in list_of_lists[0]))
            if not is_unique:
                raise TypeError('Elements in the header are not unique!')

            self.data = [OrderedDict(zip(self.header, row)) for row in self.data]

    def __getitem__(self, item):
        # this is for rows only
        if isinstance(item, (int, slice)):
            return self.data[item]

        # this is for columns only
        elif isinstance(item, (str, unicode)):
            return Series([row[item] for row in self.data])

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
            is_all_bool=True;
            for entry in item:
                if not isinstance(entry,bool):
                    is_all_bool=False;
            if is_all_bool:
                filtered_list=[]
                for index,value in enumerate(item):
                    if value:
                        filtered_list.append(self.data[index])
                return filtered_list
                      # return [[row[column_name] for column_name in item] for row in self.data]
            else:
                return [[row[column_name] for column_name in item] for row in self.data]

    def get_rows_where_column_has_value(self, column_name, value, index_only=False):
        if index_only:
            return [index for index, row_value in enumerate(self[column_name]) if row_value == value]
        else:
            return [row for row in self.data if row[column_name] == value]

    @staticmethod
    # Class method to return the type of a data object - Returns int or str or datetime
    def get_type_of_object(data_object):
        is_int = True
        try:
            if not isinstance(int(data_object), int):
                   is_int = False
        except ValueError:
                is_int = False
        if is_int:
            return int
        else:
            # Checking if all items of the column are dates
            is_date = True
            if isinstance(data_object, int):
                is_date = False
            else:
                try:
                    if not (isinstance(datetime.datetime.strptime(col, '%m/%d/%y %H:%M'), datetime.datetime)):
                        is_date = False
                except ValueError:
                        is_date = False
                if is_date:
                    return datetime
                else:
                    return str

    # ***********************Task-1********************************************************************
    def sort_by(self, column_reference, reverse):
        sorted_data=[]

        # When self.data is to be sorted based on a list of columns and reversal booleans
        if isinstance(column_reference,list) and isinstance(reverse,list):
            for index,col_name in enumerate(reversed(column_reference)):
                    col_list = [row[col_name] for row in self.data]
                    col_type = DataFrame.get_type_of_column(col_list, False)
                    data_to_sort=self.data
                    if len(sorted_data) > 0:
                         data_to_sort=sorted_data
                    if col_type == int:
                         sorted_data= sorted(data_to_sort, key=lambda k: int(k[col_name]),reverse=reverse[index])
                    elif col_type == datetime:
                         sorted_data = sorted(data_to_sort, key=lambda k: datetime.datetime.strptime(k[col_name], '%m/%d/%y %H:%M'), reverse=reverse[index])
                    # convert each string to lowercase to avoid sorting based on case sensitiveness
                    else:
                         sorted_data = sorted(data_to_sort, key=lambda k: str(k[col_name]).lower(), reverse=reverse[index])
            return sorted_data

        # When self.data is to be sorted based on a column_name and a reversal boolean
        else:
            col_list = [row[column_reference] for row in self.data]
            col_type = DataFrame.get_type_of_column(col_list, False)
            data_to_sort = self.data
            if len(sorted_data) > 0:
                data_to_sort = sorted_data
            if col_type == int:
                sorted_data = sorted(data_to_sort, key=lambda k: int(k[column_reference]), reverse=reverse)
            elif col_type == datetime:
                sorted_data = sorted(data_to_sort,
                                     key=lambda k: datetime.datetime.strptime(k[column_reference], '%m/%d/%y %H:%M'),
                                     reverse=reverse)
            # convert each string to lowercase to avoid sorting based on case sensitiveness
            else:
                sorted_data = sorted(data_to_sort, key=lambda k: str(k[column_reference]).lower(), reverse=reverse)
        return sorted_data

            # Another way of sorting a dataframe
            # Usage of indices to sort a dataframe later
            # ************************************************************
            # col_list = [row[column_reference] for row in self.data]
            # col_type = DataFrame.get_type_of_column(col_list, False)
            # sorted_list = []
            # if col_type == int:
            #     col_list = [int(i) for i in col_list]
            # sorted_indices_list = sorted(((row_value, row_number) for row_number, row_value in enumerate(col_list)),
            #                              reverse=reverse)
            # for sorted_entry in sorted_indices_list:
            #     sorted_list.append(self.data[sorted_entry[1]])
            # self.data = sorted_list
            # return sorted_list


    # ***********************End of Task-1*************************************************************

    # *********************** Task-3*************************************************************

    def group_by(self, group_by_parameter, column_2, operation):
        col_list_1 = [row[group_by_parameter] for row in self.data]
        col_list_2 = [row[column_2] for row in self.data]

        col_2_type= self.get_type_of_column(col_list_2,True)
        pairs = defaultdict(str)

        for index,entry in enumerate(col_list_1):
            pairs[entry]= col_list_2[index]

        grouped_list=[]
        grouped_list.append([group_by_parameter, str(operation.__name__+'(' + column_2 + ')')])
        for key in pairs.keys():
            agg_list=[]
            operation_list = []
            operation_list.append(key)
            for index,entry in enumerate(col_list_2):
                if col_list_1[index] == key:
                    agg_list.append(col_2_type(entry))
            operation_list.append(operation(agg_list))
            grouped_list.append(operation_list)


        grouped_data = DataFrame(grouped_list)
        return grouped_data


    # ***********************End of Task-3*************************************************************

class Series(list):
    def __init__(self, list_of_values):
        self.data = list_of_values

    def __eq__(self, other):
        ret_list = []
        data_type=DataFrame.get_type_of_object(other)
        for item in self.data:
            ret_list.append(data_type(item) == data_type(other))
        return ret_list

    def __ge__(self, other):
        ret_list = []
        data_type = DataFrame.get_type_of_object(other)
        for item in self.data:
            ret_list.append(data_type(item) >= data_type(other))
        return ret_list

    def __gt__(self, other):
        ret_list = []
        data_type = DataFrame.get_type_of_object(other)
        for item in self.data:
            ret_list.append(data_type(item) > data_type(other))
        return ret_list

    def __lt__(self, other):
        ret_list = []
        data_type = DataFrame.get_type_of_object(other)
        for item in self.data:
            ret_list.append(data_type(item) < data_type(other))
        return ret_list

    def __le__(self, other):
        ret_list = []
        data_type = DataFrame.get_type_of_object(other)
        for item in self.data:
            ret_list.append(data_type(item) <= data_type(other))
        return ret_list


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

# ******************* Task-1 *************************************
#Call to sort using a column_name and a reversal boolean- int
s1=df.sort_by('Price',True)
print s1

#Call to sort using a column_name and a reversal boolean- str
s2=df.sort_by('Name',True)
print s2

#Call to sort using a column_name and a reversal boolean- datetime
s3=df.sort_by('Transaction_date',True)
print s3

#Call to sort using a list of column_names and reversal booleans
s4=df.sort_by(['Transaction_date','Price','Name'],[False,False,False])
print df.data


# ******************* Task-2 *************************************
#To return a series with data containing column_name 'Price'
ser1=df['Price']
print ser1

#To return a series with data containing an expression data[column_name] == boolean to return a series of booleans
ser2=df['Price']==1200
print ser2

#To return a series with data containing an expression data[column_name] > boolean to return a series of booleans
ser3=df['Price']>1200
print ser3

#To return a series with data containing an expression data[column_name] < boolean to return a series of booleans
ser4=df['Price']<1200
print ser4

#To return a series with data containing an expression data[column_name] >= boolean to return a series of booleans
ser5=df['Price']>=1200
print ser5

#To return a series with data containing an expression data[column_name] <= boolean to return a series of booleans
ser6=df['Price']<=1200
print ser6

#To return a series with data containing an expression data[column_name] <= boolean to return a series of booleans
ser7=df[df['Price'] > 1400]
print ser7

# ******************* Task-3 *************************************


def avg(list_of_values):
    return sum(list_of_values) / float(len(list_of_values))

gb1=df.group_by('Payment_Type', 'Price', avg)
print gb1.data

gb1=df.group_by('Product', 'Price', avg)
print gb1.data

