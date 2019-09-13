import pandas as pd
import numpy as np
import cvxpy
import random
import operator

from constants import ROSTER, BUDGET, CONTEST_ID, N_LINEUPS, MAX_OVERLAP

def get_constraints(n_todraft, roster_todraft, player_pool, budget, selection,
                    costs):
            
    constraints = []
    # constraint 1
    # players selected must equal number starters remaining to draft
    con_num = sum(selection) == n_todraft
    constraints.append(con_num)
    
    # create position boolean arrays
    qb = np.array(player_pool['pos'] == 'QB').astype(int)
    rb = np.array(player_pool['pos'] == 'RB').astype(int)
    wr = np.array(player_pool['pos'] == 'WR').astype(int)
    te = np.array(player_pool['pos'] == 'TE').astype(int)
    flex = np.array(player_pool['pos'].isin(['RB', 'WR', 'TE'])).astype(int)
    dst = np.array(player_pool['pos'] == 'DST').astype(int)
    
    # constraint 2
    # qb selected must equal number of qb slots
    con_qb = qb * selection == roster_todraft['qb']
    constraints.append(con_qb)

    # constraint 3
    # rb selected must be at least number of rb slots 
    con_rb = rb * selection >= roster_todraft['rb']
    constraints.append(con_rb)

    # constraint 4
    # wr selected must be at least number of wr slots 
    con_wr = wr * selection >= roster_todraft['wr']
    constraints.append(con_wr)

    # constraint 5
    # te selected must be at least number of te slots
    con_te = te * selection >= roster_todraft['te']
    constraints.append(con_te)

    # constraint 6
    # dst selected must equal number of dst slots
    con_dst = dst * selection == roster_todraft['dst']
    constraints.append(con_dst)

    
    # constraint 7, 8, 9
    # rb selected cannot exceed number of rb + flex slots remaining
    con_rb_flex = rb * selection <= (roster_todraft['rb'] + roster_todraft['flex'])
    # wr selected cannot exceed number of wr + flex slots remaining
    con_wr_flex = wr * selection <= (roster_todraft['wr'] + roster_todraft['flex'])
    # te selected cannot exceed number of te + flex slots remaining
    con_te_flex = te * selection <= (roster_todraft['te'] + roster_todraft['flex'])
    constraints.extend([con_rb_flex, con_wr_flex, con_te_flex])
    
    # constraint 10: total costs less than or equal to allowed budget
    con_budget = costs * selection <= budget
    constraints.append(con_budget)
    
    return constraints

def get_selection_indices(player_pool, selection, constraints, n_todraft):
    """Return indices of players selected by convex optimization."""
    
    # set costs, returns, & variable to solve for
    returns = np.array(player_pool.loc[:, rtn]).astype(int)
    total_return = returns * selection

    # define and solve problem 
    # maximize total return across all the selections, given constraints
    problem = cvxpy.Problem(cvxpy.Maximize(total_return), constraints)
    problem.solve()
    sel_index = (-selection.value).flatten().argsort().tolist()[0][:n_todraft]
    return sel_index

def get_lineup_ids(index_list):
    ids = []
    for i in index_list:
        pos = player_pool.iloc[i]['pos'].upper()
        id = player_pool.iloc[i]['pool_id']
        ids.append(id)
    return ids

def lineup_from_ids(lineup_ids):
    pos_max = {'RB': 2, 'WR': 3, 'TE': 1}
    players = player_pool[player_pool['pool_id'].isin(lineup_ids)]
    lineup = {'QB': [], 'RB': [], 'WR': [], 'TE': [], 'FLEX': [], 'DST': []}
    for pos in ['QB', 'RB', 'WR', 'TE', 'DST']:
        pos_ids = players[players['pos'] == pos]['pool_id'].values
        if pos in pos_max.keys() and len(pos_ids) > pos_max[pos]:
            lineup[pos].extend(pos_ids[:-1])
            lineup['FLEX'].append(pos_ids[-1])
        else:
            lineup[pos].extend(pos_ids)
    return lineup
    
def list_from_lineup(lineup):
    lineup_list = []
    for pos in ['QB', 'RB', 'WR', 'TE', 'FLEX', 'DST']:
        lineup_list.extend(lineup[pos])
    return lineup_list

def get_name(id_number, player_dict):
    name = player_dict[id_number]['name']
    return name

# import cheat sheet file with player data 
data_in = "data/"
df = pd.read_csv(data_in + 'pool.csv')

# remove missing salary rows
df = df[df['cst_fd'].notnull()]

# remove bottom half defenses
dst = df[df['pos'] == 'DST']
dst_cut = dst.shape[0] / 2
dst_cut_id = dst.iloc[dst_cut:, ]['pool_id'].values

df = df[~df['pool_id'].isin(dst_cut_id)]


# set budget
budget = BUDGET
roster_todraft = ROSTER
n_start = sum(ROSTER.values())
lineups_toget = N_LINEUPS
lineups_got = 0

# name column to sum for the maximization function 
rtn = 'fp_fd'


lineups = []
lineups_unique = []
lineups_ids = []

while lineups_got < lineups_toget:

    # copy of cheatsheet data to update during nomination
    player_pool = df.copy()

    # set exposure limits
    id_count = {}
    id_prop = {}
    used = set(x for l in lineups_unique for x in l)
    for id in used:
        n = sum(list(l).count(id) for l in lineups_unique)
        id_count[id] = n
        id_prop[id] = float(n) / float(len(lineups_unique))
    
    for k in id_prop.keys():
        if id_prop[k] > 0.20:
            player_pool = player_pool.loc[player_pool['pool_id'] != k]
    
    costs = np.array(player_pool.loc[:, 'cst_fd']).astype(int)
    selection = cvxpy.Bool(len(costs))
    
    new_lineup = False
    
    while new_lineup == False:

        # get indices of players to select
        constraints = get_constraints(n_start, roster_todraft,
                                      player_pool, budget, selection,
                                      costs)
        sel_index = get_selection_indices(player_pool, selection,
                                          constraints, n_start)
        lineup = player_pool.iloc[sel_index, :].sort_values('pos')
        lineup_ids = lineup['pool_id'].values
        
        overlaps = []
        for lu in lineups_unique:
            nov = len(set(lineup_ids) & set(lu))
            overlaps.append(nov)

        if any(x > MAX_OVERLAP for x in overlaps):
            id_remove = random.choice(lineup_ids)
            player_pool = player_pool.loc[player_pool['pool_id'] != id_remove]
            costs = np.array(player_pool.loc[:, 'cst_fd']).astype(int)
            selection = cvxpy.Bool(len(costs))    
        else:
            new_lineup = True
    
    print "Lineup %s" % (lineups_got + 1)
    print lineup
    lineups_unique.append(lineup_ids)
    lineups_got += 1
    #lineup_ids = get_lineup_ids(sel_index)
    lineups.append(list_from_lineup(lineup_from_ids(lineup_ids)))

cols_tmp = ['QB', 'RB', 'RB', 'WR', 'WR', 'WR', 'TE', 'FLEX', 'DEF']
df_tmp = pd.DataFrame(lineups, columns = cols_tmp)
f_tmp = "".join(['FanDuel-NFL-', CONTEST_ID, '-lineup-upload-template.csv'])
df_tmp.to_csv(f_tmp, index=False)

sorted_used = sorted(id_prop.items(), key=operator.itemgetter(1), reverse=True)

id_name = df[['pool_id', 'name']].set_index('pool_id').to_dict('index')

for id_prop in sorted_used:
    id = id_prop[0]
    print id_name[id]['name'], round(id_prop[1], 2)
