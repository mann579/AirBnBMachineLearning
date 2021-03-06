# -*- coding: utf-8 -*-
"""airbnbdata.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VMKyRS9Ou0bv3YeyzC4lkhw602B0xUk-

Importing all libraries
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import scipy.stats as stats
import seaborn as sns
import gzip
import os
import shutil
import matplotlib.font_manager as font_manager
from sklearn.linear_model import LinearRegression, Lasso, LassoCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

"""loading the dataset"""

!wget http://data.insideairbnb.com/united-states/ny/new-york-city/2020-10-05/data/listings.csv.gz
os.rename("listings.csv.gz", "/content/listings.csv.gz")
shutil.move("listings.csv.gz", "/content/listings.csv.gz")
os.replace("listings.csv.gz", "/content/listings.csv.gz")

"""Unzipping the file"""

with gzip.open('/content/listings.csv.gz', 'rb') as f_in:
    with open('/content/listings.csv', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

"""Reading the data"""

data = pd.read_csv('/content/listings.csv')
data.shape

"""Dropping the unneccesary fields and cleaning the data"""

data = data.drop(['id','listing_url','scrape_id','last_scraped','name','neighborhood_overview','picture_url','host_id','host_url','host_name',
                  'host_since','host_location','host_about','host_is_superhost','host_thumbnail_url','host_picture_url','host_listings_count',
                  'host_verifications','host_has_profile_pic','calendar_last_scraped','first_review','last_review',
                  'calculated_host_listings_count','calculated_host_listings_count_entire_homes','calculated_host_listings_count_private_rooms',
                  'calculated_host_listings_count_shared_rooms','license','bathrooms', 'calendar_updated', 'has_availability','host_total_listings_count',
                  'minimum_nights','maximum_nights','minimum_minimum_nights','maximum_minimum_nights','minimum_maximum_nights','maximum_maximum_nights',
                  'minimum_nights_avg_ntm','maximum_nights_avg_ntm','number_of_reviews_ltm','number_of_reviews_l30d'], 
                axis=1)
data.dtypes

"""Converting 'Instant bookable' field to Int """

data.loc[data['instant_bookable'] == 'f',['instant_bookable']] = '0'
data.loc[data['instant_bookable'] == 't',['instant_bookable']] = '1'
data.instant_bookable = data.instant_bookable.astype(int)

"""Converting 'Host responce rate' field to Float"""

data['host_response_rate'] = data['host_response_rate'].str.replace("%", "").astype("float")
data['host_response_rate'].fillna(value=np.mean(data['host_response_rate']), inplace=True)

"""Cleaning the price field """

data['price'] = data['price'].str.replace('$', '')
data['price'] = data['price'].str.replace(',', '')
data["price"] = pd.to_numeric(data["price"], downcast="float")
data = data[data.price > 0]
data.isnull().sum().sort_values(ascending=False)
data.describe()

"""Changing values for 'Host identity verified' field from 'True/False' to 0/1 """

data.loc[data['host_identity_verified'] == 'f',['host_identity_verified']] = '0'
data.loc[data['host_identity_verified'] == 't',['host_identity_verified']] = '1'
data.instant_bookable = data.instant_bookable.astype(int)
data['host_identity_verified'].fillna(0, inplace=True)

data.shape

"""Price outlier Analysis """

sns.distplot(data['price'], kde=True,);
fig = plt.figure()
res = stats.probplot(data['price'], plot=plt)
print("Skewness: %f" % data['price'].skew())
print("Kurtosis: %f" % data['price'].kurt())

data = data[data.price <= 600]
data.shape

sns.distplot(data['price'], kde=True,);
fig = plt.figure()
res = stats.probplot(data['price'], plot=plt)
print("Skewness: %f" % data['price'].skew())
print("Kurtosis: %f" % data['price'].kurt())

"""Cleaning the bedroom field"""

data['bedrooms'].fillna(0, inplace=True)
data.fillna(0, inplace=True)
data = data[data.beds > 0]
data.loc[data['bedrooms'] == 0, 'bedrooms'] = 1.0
data.head()

data.isnull().sum()

"""Categorical data for neighbourhood """

data['neighbourhood_group_cleansed'].unique()

labels = data.neighbourhood_group_cleansed.value_counts().index
colors = ['#008fd5','#fc4f30','#e5ae38','#6d904f','#8b8b8b']

shape = data.neighbourhood_group_cleansed.value_counts().values
plt.figure(figsize=(8,8))
plt.pie(shape, labels=shape, colors= colors, autopct = '%1.1f%%', startangle=90)
plt.legend(labels)
plt.title('Neighbourhood Group')
plt.show()

"""Categorical data for room types"""

labels = data.room_type.value_counts().index

colors = ['#008fd5','#fc4f30','#e5ae38','#6d904f']

shape = data.room_type.value_counts().values

plt.figure(figsize=(8,8))
plt.bar(labels, shape, color=colors)
plt.title('Room type')
plt.show()

"""Corelation matrix """

corr_matrix = abs(data.corr())
plt.figure(figsize=(20,20))
title = 'Correlation matrix of data'
sns.heatmap(corr_matrix,linewidths=0.25,vmax=1.0, square=True, cmap='RdYlGn',annot=True)
plt.title(title)
plt.ioff()

corr_matrix['price'].sort_values(ascending=False)

"""Applying Lasso"""

newData = data.select_dtypes(exclude='object')
newData.fillna(0, inplace=True)
newData.isnull().sum()

X = newData.iloc[:, newData.columns != 'price']
Y = newData.iloc[:, newData.columns == 'price']
Y

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size = 0.2, random_state = 0)
std = StandardScaler()
std.fit(X_train.values)
X_tr_train = std.transform(X_train.values)
X_tr_test = std.transform(X_test.values)

alphavec = 10**np.linspace(-2,2,200)
lasso_model_census = LassoCV(alphas = alphavec, cv=5)
lasso_model_census.fit(X_tr_train, y_train)

lasso_betas = list(zip(X_train.columns,
lasso_model_census.coef_))# R2 of Training set
lasso_model_census.score(X_tr_train,y_train)

lasso_betas

y_pred = lasso_model_census.predict(X_tr_test)
y_pred = y_pred.reshape(len(y_pred), 1)
r2_score(y_test, y_pred)
def mae(y_true, y_pred):
    return np.mean(np.abs(y_pred - y_true))
    
mae(y_test, y_pred)
plt.scatter(y_test, y_pred)
plt.plot([0,10],[0,10],color='red')
plt.grid(True)
plt.title('Predicted vs. Actual Price with LASSO')
plt.ylabel('Rental Price Predicted')
plt.xlabel('Rental Price Actual');

"""Taking the important fields affecting Prices"""

X = data.loc[:,['accommodates','bedrooms','beds','availability_365','review_scores_rating', 'review_scores_accuracy','review_scores_value', 'instant_bookable', 'reviews_per_month']].values
y = data['price'].values
y = np.log10(y)

"""Seperating the data into Train and Test set"""

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)

"""Linear regression Model"""

from sklearn.linear_model import LinearRegression
linear_reg = LinearRegression()
linear_reg.fit(X_train, y_train)
y_pred = linear_reg.predict(X_test)
y_test.shape

lr_matrix = pd.DataFrame({'Actual': np.round(10 ** y_test, 0), 
                       'Predicted': np.round(10 ** y_pred, 0)})
lr_matrix.head(10)

from sklearn.metrics import mean_squared_error
from sklearn import metrics
from sklearn.metrics import r2_score
print('Price mean:', np.round(np.mean(y), 2))  
print('Price std:', np.round(np.std(y), 2))
print('RMSE:', np.round(np.sqrt(metrics.mean_squared_error(y_test, linear_reg.predict(X_test))), 2))
print('R2 score train:', np.round(r2_score(y_train, linear_reg.predict(X_train), multioutput='variance_weighted'), 2))
print('R2 score test:', np.round(r2_score(y_test, linear_reg.predict(X_test), multioutput='variance_weighted'), 2))

"""Ridge Regression Model"""

from sklearn.linear_model import Ridge
ridge_reg = Ridge(alpha=1.0)
ridge_reg.fit(X_train, y_train)
y_pred = ridge_reg.predict(X_test)

print('Price mean:', np.round(np.mean(y), 2))  
print('Price std:', np.round(np.std(y), 2))
print('RMSE:', np.round(np.sqrt(metrics.mean_squared_error(y_test, ridge_reg.predict(X_test))), 2))
print('R2 score train:', np.round(r2_score(y_train, ridge_reg.predict(X_train), multioutput='variance_weighted'), 2))
print('R2 score test:', np.round(r2_score(y_test, ridge_reg.predict(X_test), multioutput='variance_weighted'), 2))

"""Support Vector Regression"""

from sklearn.svm import SVR
svr_regressor = SVR(kernel='rbf')
svr_regressor.fit(X_train,y_train)
y_pred = svr_regressor.predict(X_test)

print('Price mean:', np.round(np.mean(y), 2))  
print('Price std:', np.round(np.std(y), 2))
print('RMSE:', np.round(np.sqrt(metrics.mean_squared_error(y_test, svr_regressor.predict(X_test))), 2))
print('R2 score train:', np.round(r2_score(y_train, svr_regressor.predict(X_train), multioutput='variance_weighted'), 2))
print('R2 score test:', np.round(r2_score(y_test, svr_regressor.predict(X_test), multioutput='variance_weighted'), 2))

"""Random forest method model"""

from sklearn.ensemble import RandomForestRegressor
rf_reg = RandomForestRegressor(max_depth=8, n_estimators = 100, random_state = 0)
rf_reg.fit(X_train, y_train)
y_pred = rf_reg.predict(X_test)
y_pred

rf_matrix = pd.DataFrame({'Actual': np.round(10 ** y_test, 0), 
                   'Predicted': np.round(10 ** y_pred, 0)})
rf_matrix.head(10)

print('Price mean:', np.round(np.mean(y), 2))  
print('Price std:', np.round(np.std(y), 2))
print('RMSE:', np.round(np.sqrt(metrics.mean_squared_error(y_test, rf_reg.predict(X_test))), 2))
print('R2 score train:', np.round(r2_score(y_train, rf_reg.predict(X_train), multioutput='variance_weighted'), 2))
print('R2 score test:', np.round(r2_score(y_test, rf_reg.predict(X_test), multioutput='variance_weighted'), 2))

"""XGBoost Regression Model"""

import xgboost as xgb
from sklearn.preprocessing import StandardScaler
stan_sc = StandardScaler()
X_train = stan_sc.fit_transform(X_train)
X_test  = stan_sc.transform(X_test)

from sklearn.model_selection import GridSearchCV
xg_booster = xgb.XGBRegressor()
param_grid = {'n_estimators': [100, 150, 200],
              'learning_rate': [0.01, 0.05, 0.1], 
              'max_depth': [3, 4, 5, 6, 7],
              'colsample_bytree': [0.6, 0.7, 1],
              'gamma': [0.0, 0.1, 0.2]}

grid_search = GridSearchCV(xg_booster, param_grid, cv=3, n_jobs=-1)

grid_search.fit(X_train, y_train)
print(grid_search.best_params_)

xg_booster = xgb.XGBRegressor(colsample_bytree=0.7, gamma=0.4, learning_rate=0.5, 
                           max_depth=6, n_estimators=200, random_state=4)
xg_booster.fit(X_train, y_train)
y_pred = xg_booster.predict(X_test)

print('Price mean:', np.round(np.mean(y), 2))  
print('Price std:', np.round(np.std(y), 2))
print('RMSE:', np.round(np.sqrt(metrics.mean_squared_error(y_test, xg_booster.predict(X_test))), 2))
print('R2 score train:', np.round(r2_score(y_train, xg_booster.predict(X_train), multioutput='variance_weighted'), 2))
print('R2 score test:', np.round(r2_score(y_test, xg_booster.predict(X_test), multioutput='variance_weighted'), 2))