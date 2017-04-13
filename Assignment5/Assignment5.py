from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import datetime
from time import strftime
import unicodedata
import time
import pandas as pd
from datetime import timedelta
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler,RobustScaler,MinMaxScaler
import numpy as np
import statistics
import matplotlib.pyplot as plt
from scipy.spatial import distance
from scipy.spatial.distance import euclidean
from collections import OrderedDict
import pandas as pd

class FlightsExplore:
    driver_location = 'C:\Praveen\_PG\_STEVENS\BIA_Web_Analytics\MISC\chromedriver_win32\chromedriver'
    google_explore_path = 'https://www.google.com/flights/explore/#explore'
    from_elem_xpath = '//*[@id="root"]/div[3]/div[3]/div/div[2]'
    to_elem_path = '//*[@id="root"]/div[3]/div[3]/div/div[4]'
    date_of_flight=[]

    # ************* Task - 1 ******************************************
    @staticmethod
    def scrape_data(start_date, from_place, to_place, city_name):

        # Create driver for chrome to parse through flights explore date
        driver = webdriver.Chrome(FlightsExplore.driver_location)
        driver.get(FlightsExplore.google_explore_path)
        from_elem = driver.find_element_by_xpath(FlightsExplore.from_elem_xpath)
        from_elem.click()

        # Create Action keys to select and modify entries within a textbox
        from_action = ActionChains(driver)
        from_action.send_keys(u'\ue005')
        from_action.send_keys(from_place+'(All airports)')
        from_action.send_keys(Keys.ENTER)
        from_action.perform()
        to_elem = driver.find_element_by_xpath(FlightsExplore.to_elem_path)
        to_elem.click()
        to_action = ActionChains(driver)
        to_action.send_keys(u'\ue005')
        to_action.send_keys(to_place)
        to_action.send_keys(Keys.ENTER)
        to_action.perform()
        time.sleep(5)
        required_date = start_date.strftime("%Y-%m-%d")
        url_part_1 = p1=driver.current_url.split('d=')[0]
        driver.get(url_part_1+"d="+required_date)
        time.sleep(5)

        # Parse through each flight bar and retrieve price results for corresponding dates
        flight_cols = ['Date_Of_Flight','Price']
        flight_block_elements = driver.find_elements_by_class_name('LJTSM3-v-d')
        flight_data = []
        for flight_block in flight_block_elements:
            time.sleep(1)
            time.sleep(1)
            city_result = flight_block.find_elements_by_class_name('LJTSM3-v-c')[0].text.split(',')[0]
            city_decoded = ''.join(word for word in unicodedata.normalize('NFD', city_result) if unicodedata.category(word) != 'Mn')
            if city_decoded.lower() in city_name.lower():
                flight_bars = flight_block.find_elements_by_class_name('LJTSM3-w-x')
                for f_bar in flight_bars:
                    ActionChains(driver).move_to_element(f_bar).perform()
                    dates = flight_block.find_element_by_class_name('LJTSM3-w-k').find_elements_by_tag_name('div')[1].text
                    price = flight_block.find_element_by_class_name('LJTSM3-w-k').find_elements_by_tag_name('div')[0].text
                    flight_data.append([str(dates.split('-')[0]).strip(),str(price)])
        return pd.DataFrame.from_records(flight_data,columns=flight_cols)

    # ************* Task - 2 ******************************************
    # Scrape data for 90 consecutive days
    # Method here is to call the scrape function for 60 days twice
    # Then later remove the last 30 from the combined set
    @staticmethod
    def scrape_data_90(start_date, from_place, to_place, city_name):
        df_first_60 = FlightsExplore.scrape_data(start_date, from_place, to_place, city_name)
        date_60_later = start_date + timedelta(days=60)
        df_next_60 = FlightsExplore.scrape_data(date_60_later, from_place, to_place, city_name)
        df_next_30 = df_next_60.iloc[:30, :]
        list_frames = [df_first_60, df_next_30]
        merged_frame = pd.concat(list_frames)
        merged_frame.index = range(len(merged_frame))
        return merged_frame

    # Concatenates days and prices data
    @staticmethod
    def make_x(days, prices):
        return np.concatenate([days, prices], axis=1)

    # Calculates means for all clusters
    @staticmethod
    def calculate_cluster_means(x, labels):
        unique_labels = np.unique(labels)
        cluster_means = [np.mean(x[labels == num, :], axis=0) for num in unique_labels if num != -1]
        return cluster_means

    # ************* Task - 3 ******************************************
    # Perform DB-Scan with appropriate epsilon and minimum samples per cluster value
    @staticmethod
    def task_3_dbscan(flight_data):
        flight_data_list = []

        # Extracting date and price in required format
        for i in range(len(flight_data)):
            date_entry = flight_data.loc[i]['Date_Of_Flight']
            price_entry = flight_data.loc[i]['Price']
            if str(date_entry).strip() != '':
                FlightsExplore.date_of_flight.append(date_entry)
                date_num = (datetime.datetime.now() - datetime.datetime.strptime(date_entry, "%a %b %d")).days
            if str(price_entry).strip() != '':
                price_num = float(price_entry.replace('$', '').replace(',', ''))
                flight_data_list.append((i + 1, price_num))

        # Converting date and price into a data frame
        cleaned_flight_df = pd.DataFrame(flight_data_list, columns=['Start_Date', 'Price'])
        df = pd.DataFrame(cleaned_flight_df, columns=['Price', 'Start_Date'])
        prices_min_max_scaled = MinMaxScaler(feature_range=(-1.75, 1.75)).fit_transform(cleaned_flight_df['Price'][:, None])
        days_min_max_scaled = MinMaxScaler(feature_range=(-3, 3)).fit_transform(cleaned_flight_df['Start_Date'][:, None])
        x_values_scaled = FlightsExplore.make_x(days_min_max_scaled, prices_min_max_scaled)

        # Using different epsilon and minimum sample values for different lengths of data
        if len(x_values_scaled)>60:
            epsilon = 0.275
            minimum_samples_per_cluster = 4
        else:
            epsilon = 0.3
            minimum_samples_per_cluster = 3

        # Performing DB-Scan method on existing data
        db = DBSCAN(epsilon,minimum_samples_per_cluster).fit(x_values_scaled)
        labels = db.labels_
        clusters = len(set(labels))
        if -1 in set(labels):
            clusters -= 1
        unique_labels = set(labels)
        colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
        plt.subplots(figsize=(10, 5))
        for k, c in zip(unique_labels, colors):
            class_member_mask = (labels == k)
            xy = x_values_scaled[class_member_mask]
            plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=c, markeredgecolor='k', markersize=14)
        plt.title("Total Clusters:{} Eps:{} Mins:{}".format(clusters, epsilon, minimum_samples_per_cluster), fontsize=14, y=1.01)
        df['dbscan_labels'] = db.labels_
        # Save the plot with required name
        plt.savefig("task_3_dbscan.png")
        plt.show()

        # Calculating the means of all clusters
        cluster_means = FlightsExplore.calculate_cluster_means(x_values_scaled, labels)
        indices_of_outliers = []
        for scaled_x_co_ordinate_index,y in enumerate(x_values_scaled):
            if labels[scaled_x_co_ordinate_index] == -1:
                indices_of_outliers.append([scaled_x_co_ordinate_index,y])

        # Finding means and standard deviations of all clusters
        indices_of_clusters = []
        for each_cluster in set(labels):
            price_list=[]
            if each_cluster != -1:
                for scaled_x_co_ordinate_index, y in enumerate(x_values_scaled):
                    if labels[scaled_x_co_ordinate_index] == each_cluster:
                        price_list.append(cleaned_flight_df['Price'][scaled_x_co_ordinate_index])
                indices_of_clusters.append({each_cluster: [statistics.mean(price_list),statistics.stdev(price_list)]})

        # Find list of outliers and corresponding closest cluster means
        outlier_coordinate_indices = x_values_scaled[labels == -1]
        outlier_index_with_cluster_index_list = []
        for outlier_index, outlier_cods in enumerate(outlier_coordinate_indices):
            min_list = []
            for cluster_index, cluster_mean_cods in enumerate(cluster_means):
                min_list.append(euclidean(cluster_mean_cods, outlier_cods))
            for inx, abc in enumerate(min_list):
                if abc == sorted(min_list)[0]:
                    outlier_index_with_cluster_index_list.append([outlier_index, inx])

        # Finding mistake prices that satisfy requirements
        cluster_labels = unique_labels
        if -1 in cluster_labels:
            cluster_labels.remove(-1)
        mistake_price_list = []
        mistake_price_cols = ['Date_Of_Flight','Price']
        for i, abc in enumerate(indices_of_outliers):
            outlier_price = df['Price'][abc[0]]
            outlier_date = FlightsExplore.date_of_flight[abc[0]]
            closest_cluster = sorted(cluster_labels)[outlier_index_with_cluster_index_list[i][1]]
            mean_closest_cluster = indices_of_clusters[closest_cluster].get(closest_cluster)[0]
            std_closest_cluster = indices_of_clusters[closest_cluster].get(closest_cluster)[1]
            if (outlier_price < (mean_closest_cluster-(2*std_closest_cluster))) and (mean_closest_cluster-outlier_price)>50:
                mistake_price_list.append([outlier_date,outlier_price])

        return pd.DataFrame(mistake_price_list,columns=mistake_price_cols)

    # ************* Task - 4 ******************************************
    @staticmethod
    def task_4_dbscan(flight_data):
        flight_data_list = []
        # find flight data after extraction
        for i in range(len(flight_data)):
            date_entry = flight_data.loc[i]['Date_Of_Flight']
            price_entry = flight_data.loc[i]['Price']
            if str(date_entry).strip() != '':
                FlightsExplore.date_of_flight.append(date_entry)
            if str(price_entry).strip() != '':
                price_num = float(price_entry.replace('$', '').replace(',', ''))
                flight_data_list.append((i + 1, price_num))
        cleaned_flight_df = pd.DataFrame(flight_data_list, columns=['Start_Date', 'Price'])
        df = pd.DataFrame(cleaned_flight_df, columns=['Price', 'Start_Date'])


        prices_min_max_scaled = MinMaxScaler(feature_range=(-6, 6)).fit_transform(
            cleaned_flight_df['Price'][:, None])
        days_min_max_scaled = MinMaxScaler(feature_range=(-3, 3)).fit_transform(
            cleaned_flight_df['Start_Date'][:, None])
        x_values_scaled = FlightsExplore.make_x(days_min_max_scaled, prices_min_max_scaled)

        # Choosing different epsilon values
        minimum_samples_per_cluster = 5
        if len(x_values_scaled) > 60:
            epsilon = 0.3
        else:
            epsilon = 0.4
        # Plot the DB-Scan for data
        db = DBSCAN(epsilon, minimum_samples_per_cluster).fit(x_values_scaled)
        labels = db.labels_
        clusters = len(set(labels))
        if -1 in set(labels):
            clusters -= 1
        unique_labels = set(labels)
        colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
        plt.subplots(figsize=(10, 5))
        for k, c in zip(unique_labels, colors):
            class_member_mask = (labels == k)
            xy = x_values_scaled[class_member_mask]
            plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=c, markeredgecolor='k', markersize=14)
        plt.title("Total Clusters:{} Eps:{} Mins:{}".format(clusters, epsilon, minimum_samples_per_cluster), fontsize=14, y=1.01)
        df['dbscan_labels'] = db.labels_
        plt.show()



        indices_of_clusters = []
        for each_cluster in set(labels):
            price_list = []
            date_list = []
            if each_cluster != -1:
                for scaled_x_co_ordinate_index, y in enumerate(x_values_scaled):
                    if labels[scaled_x_co_ordinate_index] == each_cluster:
                        price_list.append(cleaned_flight_df['Price'][scaled_x_co_ordinate_index])
                        date_list.append(cleaned_flight_df['Start_Date'][scaled_x_co_ordinate_index])

            if len(price_list)>1:
                if statistics.stdev(price_list) < 20:
                    condition = True
                    for index,price in enumerate(price_list):
                        add_list = []
                        for i in range(0,5):
                            if index+i+1 < len(price_list):
                                dif = abs(price_list[index+1] - price_list[index])
                                if dif > 20:
                                    condition =False
                                add_list.append([FlightsExplore.date_of_flight[date_list[index]],price_list[index]])

                        if condition:
                            print "********Printing an observed contiguous list******8"
                            print add_list


    # Finding outliers using IQR method
    @staticmethod
    def  task_3_IQR(flight_data):
        flight_price_list = []
        flight_date_list = []
        for i in range(len(flight_data)):
            date_entry = flight_data.loc[i]['Date_Of_Flight']
            flight_date_list.append(date_entry)
            price_entry = flight_data.loc[i]['Price']
            if str(price_entry).strip() != '':
                price_num = float(price_entry.replace('$', '').replace(',', ''))
                flight_price_list.append(price_num)
        q75, q25 = np.percentile(flight_price_list, [75, 25])
        iqr = q75 - q25
        mistake_prices = []
        mistake_price_cols = ['Date_Of_Flight', 'Price']
        for i,value in enumerate(flight_price_list):
            boolean_out = FlightsExplore.is_outlier(value,q25,q75)
            if boolean_out:
                mistake_prices.append([flight_date_list[i],value])
        plt.boxplot(flight_price_list, 0, 'gD')
        plt.savefig("task_3_iqr.png")
        plt.show()
        return pd.DataFrame(mistake_prices, columns=mistake_price_cols)

    # Method to return if a value is an outlier
    @staticmethod
    def is_outlier(value, p25, p75):
        lower = p25 - 1.5 * (p75 - p25)
        upper = p75 + 1.5 * (p75 - p25)
        return value <= lower or value >= upper


print 'Started...'
# flight_dataframe = FlightsExplore.scrape_data(datetime.datetime(2017, 5, 23, 0, 0),'New York City','Germany','Berlin')
flight_dataframe = FlightsExplore.scrape_data(datetime.datetime(2017, 8, 27, 0, 0),'New York City','India','Goa')
# flight_next90_dataframe = FlightsExplore.scrape_data_90(datetime.datetime(2017, 6, 27, 0, 0),'New York City','Germany','Berlin')
# # print flight_dataframe
# print 'End of 1st 60...'
# # print flight_next90_dataframe
# mistake_prices = FlightsExplore.task_3_dbscan(flight_dataframe)
# mistake_prices = FlightsExplore.task_3_dbscan(flight_next90_dataframe)
# # print mistake_prices
# FlightsExplore.task_3_IQR(flight_dataframe)
# FlightsExplore.task_3_IQR(flight_next90_dataframe)
FlightsExplore.task_4_dbscan(flight_dataframe)
# FlightsExplore.task_4_dbscan(flight_next90_dataframe)
print 'End of program...'