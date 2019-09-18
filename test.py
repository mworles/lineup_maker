import pandas as pd
import numpy as np
import itertools
import random
import seaborn as sns
import matplotlib.pyplot as plt



#import filter_players
#import assign_id

# import cheat sheet file with player data 
data_in = "data/"
df = pd.read_csv(data_in + 'pool_owned.csv')

"""
for pos in df['pos'].unique():
    print pos
    dfp = df[df['pos'] == pos]
    dfp = dfp[dfp['owned_pct'].notnull()]
    dfp = dfp[dfp['owned_pct'] > 0]
    x = dfp['owned_pct'].apply(lambda x: np.log(x))
    mn = x.mean()
    x -= mn
    sns.distplot(x, bins=10)
    plt.show()
"""
from sklearn.linear_model import LinearRegression

# %%
w = df[df['pos'] == 'WR']
w = w[w['owned_pct'].notnull()]
w = w[w['owned_pct'] > 0]
y = w['owned_pct'].apply(lambda x: np.log(x))
mn = y.mean()
y -= mn



w = w.sort_values('cst_fd', ascending=False)
w['val_rm'] = w['val_fd'].rolling(5).mean()
w['val_rm'] = w['val_rm'].fillna(method='bfill')
w['val_disp'] = w['val_fd'] - w['val_rm']
w = w.drop('val_rm', axis=1)

xcols = ['fp_fd', 'cst_fd', 'val_fd']
x = w.loc[:, xcols]


for f in xcols:
    fmn = x[f].mean()
    fsd = x[f].std()
    x[f] = (x[f] - fmn) / fsd

for c in ['cst_fd', 'val_fd']:
    cname = 'fpX' + c[0:3]
    x[cname] = x['fp_fd'] * x [c]

x['cstXval'] = x['cst_fd'] * x ['val_fd']

# sorted by salary, rolling mean of value

x = x.values

reg = LinearRegression().fit(x, y)
print reg.score(x, y)

yhat = reg.predict(x)

w['y'] = np.exp(y + mn)
w['yhat'] = np.round(np.exp(yhat + mn), 2)
w['dif'] = np.round(w['y'] - w['yhat'])
w['difabs'] = w['dif'].abs()

w = w.sort_values('difabs', ascending=False)
showcols = ['name']
showcols.extend(xcols)
showcols.extend(['y', 'yhat', 'dif'])
showcols.append('val_disp')
print w[showcols].head(50)

"""
i_range = range(1, 16)
i_range = [i_range] * 30000

def random_four(x):
    pi = np.random.choice(x, 4)
    return pi
    
lu = map(random_four, i_range)
print lu[0:10]


df = pd.read_csv('data/nf_projections.csv')

q = df[df['pos'] == 'QB']

q.sort_values('val_fd', ascending=False)


for p in df['pos'].unique():
    d = d[d['pos'] == p]
    d = df.sort_values('val_fd', ascending=False)
    print p
    print d.head(20)
"""
