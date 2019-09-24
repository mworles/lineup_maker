import pandas as pd
import numpy as np
import itertools
import random
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression, BayesianRidge
import operator

#import filter_players
#import assign_id

# import cheat sheet file with player data 
data_in = "data/"

df = pd.read_csv(data_in + 'pool_owned.csv')

pos = 'DST'
sal = 'cst_fd'
val = 'val_fd'
pts = 'fp_fd'
"""
# %%
w = df[df['pos'] == pos]
w = w[w['owned_pct'].notnull()]
w = w[w['owned_pct'] > 0]

# compute expected value and points given salary
xmat = w[sal].values.reshape(-1, 1)
w['vexp'] = LinearRegression().fit(xmat, w[val]).predict(xmat)
w['pexp'] = LinearRegression().fit(xmat, w[pts]).predict(xmat)

# compute disparity between points and salary-expected points
w['val_disp'] =  np.round(w[val] - w['vexp'], 2)

# compute disparity between points and salary-expected points
w['fp_disp'] =  np.round(w[pts] - w['pexp'], 2)

# adjust for expected points
w['fp_dispa'] = w['fp_disp'] / w['pexp']

# compute product of disparities
#w['disp2'] = w['fp_dispa'] * w['val_disp']

xcols = ['fp_fd', 'cst_fd', 'val_fd', 'val_disp', 'fp_disp', 'fp_dispa']
         #'disp2']

# define target variable
y = w['owned_pct'].apply(lambda x: np.log(x))
y_mean = y.mean()
y -= y_mean

# filter data to feature columns
w = w.loc[:, xcols]

# mean standarize feature values
for feat in xcols:
    feat_mean = w[feat].mean()
    feat_sd = w[feat].std()
    w[feat] = (w[feat] - feat_mean) / feat_sd
# 
x = w.values

# fit regression to features
reg = LinearRegression().fit(x, y)
yhat = reg.predict(x)
reg_score = mean_squared_error(y, yhat)
print reg_score
print reg.score(x, y)
"""
# import pool data
df = pd.read_csv(data_in + 'pool.csv')

# %%
newdf = []
for pos in ['QB', 'RB', 'WR', 'TE', 'DST']:
    w = df[df['pos'] == pos]
    #w = w[w[sal, val, pts].notnull()]
    w = w[w[sal].notnull()]
    w = w[w[val].notnull()]
    w = w[w[pts].notnull()]
    w = w[w[pts] > 2.0]


    # compute expected value and points given salary
    xmat = w[sal].values.reshape(-1, 1)
    w['vexp'] = LinearRegression().fit(xmat, w[val]).predict(xmat)
    w['pexp'] = LinearRegression().fit(xmat, w[pts]).predict(xmat)

    # compute disparity between points and salary-expected points
    w['val_disp'] =  np.round(w[val] - w['vexp'], 2)

    # compute disparity between points and salary-expected points
    w['fp_disp'] =  np.round(w[pts] - w['pexp'], 2)

    # adjust for expected points
    w['fp_dispa'] = w['fp_disp'] / w['pexp']
    newdf.append(w)

nd = pd.concat(newdf)
nd = nd[nd['val_disp'] > 0]
nd = nd.sort_values('fp_fd', ascending=False)
nd = nd[nd['pos'] == 'QB']
print nd.head(20)

"""
# compute product of disparities
#w['disp2'] = w['fp_dispa'] * w['val_disp']

xcols = ['fp_fd', 'cst_fd', 'val_fd', 'val_disp', 'fp_disp', 'fp_dispa']
        # 'disp2']

# mean standarize feature values
for feat in xcols:
    feat_mean = w[feat].mean()
    feat_sd = w[feat].std()
    w[feat] = (w[feat] - feat_mean) / feat_sd

# filter data to feature columns
x = w[xcols].values

yhat = reg.predict(x)

w['yhat'] = np.round(np.exp(yhat + y_mean), 2)

w['yhatp'] = w['yhat']**1.5
yhsum = w['yhatp'].sum()
w['yhatp'] = w['yhatp'] / yhsum

w = w.sort_values('yhatp', ascending=False)
showcols = ['name']
showcols.extend(xcols)
showcols.extend(['yhat', 'yhatp'])
print w[showcols].head(50)


nlu = 10000
pp = w[['name', 'yhat']]
pp['yhat'] = pp['yhat'] / 100

wrs = []
for pi in pp.index.values:
    plprop = pp.loc[pi, 'yhat']
    n_pl = int(plprop * 1000)
    wrs.extend([pi] * n_pl)

id_prop = {}
n_set = set(wrs)
for id in n_set:
    n = wrs.count(id)
    id_prop[id] = float(n) / float(len(wrs))
    
sorted_chosen = sorted(id_prop.items(), key=operator.itemgetter(1), reverse=True)
name_dict = w['name'].to_dict()

for id_prop in sorted_chosen:
    id = id_prop[0]
    print name_dict[id], round(id_prop[1], 4)

"""
