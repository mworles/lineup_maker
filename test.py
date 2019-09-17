import pandas as pd
import numpy as np
import itertools
import random

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
