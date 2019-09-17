import pandas as pd
import numpy as np
import itertools
import random

# %%
df = pd.read_csv('data/nf_projections.csv')

pos_thresh = {'RB': .70,
              'WR': .70}

df = df.sort_values('cst_fd', ascending=False)

for p in ['RB', 'WR']:
    p_drop = int(df[df['pos'] == p].shape[0] * pos_thresh[p])
    p_i = df[df['pos'] == p].iloc[p_drop:].index.values
    df = df.drop(p_i)

rb = df[df['pos'] == 'RB'].index.values
wr = df[df['pos'] == 'WR'].index.values
dst = df[df['pos'] == 'DST'].index.values

# top 20 qbs
qb = df[df['pos'] == 'QB'].sort_values('cst_fd', ascending=False).iloc[0:12].index.values

"""
# top 30 flex
flexp = ['RB', 'WR']
flx = df[df['pos'].isin(flexp)].sort_values('cst_fd', ascending=False).iloc[0:30].index.values
flx_cmb = list(itertools.combinations(flx, 2))
"""
# top 15 rb
rb = df[df['pos'] == 'RB'].iloc[0:15].index.values

# TOP 15 wr
wr = df[df['pos'] == 'WR'].iloc[0:15].index.values

# top 30 tight ends
te = df[df['pos'] == 'TE'].iloc[0:15].index.values

# top 12 dst
dst = df[df['pos'] == 'DST'].iloc[0:8].index.values

p = [qb, rb, wr, te, dst]
cores = list(itertools.product(*p))

costs = df['cst_fd'].to_dict()

def cost_of_ids(id_list):
    cost = np.sum([costs[id] for id in id_list])
    return cost

core_costs = map(cost_of_ids, cores)

core_max = np.max(core_costs)
core_min = np.min(core_costs)


extra_max = 60000 - core_min
extra_min = 60000 - core_max

rb = df[df['pos'] == 'RB'].iloc[15:, :].index.values
wr = df[df['pos'] == 'WR'].iloc[15:, :].index.values

p = [rb, rb, wr, wr]
extras = list(itertools.product(*p))

rbc = df[df['pos'] == 'RB'].iloc[15:, :]['cst_fd']
wrc = df[df['pos'] == 'WR'].iloc[15:, :]['cst_fd']

pc = [rbc, rbc, wrc, wrc]
pce = list(itertools.product(*pc))


324000*50


def add_extra(core_list):
    global extras
    tc = 65000
    while tc > 60000:
        cost = cost_of_ids(core_list)
        rest = random.choice(extras)
        extra_cost = cost_of_ids(rest)
        tc = cost + extra_cost
    return core_list + rest

y = map(add_extra, cores[0:5])
print y

"""
p = [rb, rb, wr, wr]
extras = list(itertools.product(*p))
extras_costs = map(cost_of_ids, extras)

print len(extras)
print np.max(extras_costs)
print np.min(extras_costs)
"""
"""
costs = df['cst_fd'].to_dict()
pos_dict = df['pos'].to_dict()

def is_rb(x):
    if pos_dict[x] == 'RB':
        return 1
    else:
        return 0

rb_counts = [np.sum([(is_rb(x)) for x in core[1]]) for core in cores]

rb_cores = []
wr_cores = []
split_cores = []

for x, y in zip(cores, rb_counts):
    if y == 2:
        rb_cores.append(core)
    elif y == 1:
        split_cores.append(core)
    else:
        wr_cores.append(core)


wr_comb3 = list(itertools.combinations(wr, 3))
rb1_wr3 = list(itertools.product(*[rb, wr_comb3]))

def get_cost(x):
    x_list = [x[0]]
    x_list.extend(list(x[1]))
    cost = np.sum([costs[id] for id in x_list])
    return cost
    
rb1_wr3_cst = map(get_cost, rb1_wr3)



rb1_wr3_cst[0:10]


len(rb_cores) * len(rb1_wr3_cst)

len(rb1_wr3_cst)

list((1, 2))


# %%
def lineup_from_core(x):
    lu = {'QB': [x[0]]}
    lu['TE'] = [x[2]]
    lu['DST'] = [x[3]]
    p1 = x[1][0]
    p2 = x[1][1]
    pos_p1 = df.loc[p1, 'pos']
    lu[pos_p1] = [p1]
    pos_p2 = df.loc[p2, 'pos']
    if pos_p2 in lu.keys():
        lu[pos_p2].append(p2)
    else:
        lu[pos_p2] = [p2]
        
    return lu
    
lineups = map(lineup_from_core, cores)




# %%
costs = df['cst_fd'].to_dict()

def get_cost(lineup):
    if 'cost' in lineup:
        del lineup['cost']
    ids_list = lineup.values()
    ids = [item for sublist in ids_list for item in sublist]
    lineup['cost'] = np.sum([costs[id] for id in ids])  
    lineup['bal'] = 60000 - lineup['cost']
    return lineup

get_cost(lineups[0])

lineups = map(get_cost, lineups)

lu = lineups[0]
ids_list = [x for x in lu.values() if type(x) == list]
ids = [item for sublist in ids_list for item in sublist]

p = [rb_uni, list(itertools.combinations(wr_uni, 3))]
rem = list(itertools.product(*p))

def rem_ids(x):
    rem_list = [x[0]] + list(x[1])
    return rem_list

def id_cost(ids):
    cost = np.sum([costs[id] for id in ids])  
    return cost

id_cost(rem_list)

rem_costs = map(id_cost, map(rem_ids, rem))

rem_ids(rem_list[0:10])

rem[0]

rem0 = rem[0]
lu_rem = [rem0[0]]
lu_rem.extend(list(rem0[1]))
rem_ids = ids + lu_rem
"""
