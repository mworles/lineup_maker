import pandas as pd
import numpy as np
import cvxpy
import random

from constants import ROSTER, BUDGET

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

def lineup_from_ids(index_list):
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

#def names_from_ids():
    


# import cheat sheet file with player data 
data_in = "data/"
df = pd.read_csv(data_in + 'pool.csv')

# remove missing salary rows
df = df[df['cst_fd'].notnull()]

# set budget
budget = BUDGET
roster_todraft = ROSTER
n_start = sum(ROSTER.values())
lineups_toget = 3
lineups_got = 0

# name column to sum for the maximization function 
rtn = 'fp_fd'


lineups = []
lineups_unique = []
lineups_ids = []

while lineups_got < lineups_toget:

    # copy of cheatsheet data to update during nomination
    player_pool = df.copy()
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
        if set(sel_index) not in lineups_unique:
            new_lineup = True
        else:
            p_remove = random.choice(sel_index)
            player_pool = player_pool.drop(p_remove)
            costs = np.array(player_pool.loc[:, 'cst_fd']).astype(int)
            selection = cvxpy.Bool(len(costs))

    lineup = player_pool.iloc[sel_index, :].sort_values('pos')
    print "Lineup %s" % (lineups_got + 1)
    print lineup
    lineups_unique.append(set(sel_index))
    lineups_got += 1
    lineup_ids = get_lineup_ids(sel_index)
    print player_pool[player_pool['pool_id'].isin(lineup_ids)]
    lineups.append(lineup_from_ids(lineup_ids))

lineup_list = [list_from_lineup(x) for x in lineups]


player_dict = df[['name', 'pool_id']].set_index('pool_id').to_dict('index')


one_lineup = lineup_list[0]
names = [get_name(x, player_dict) for x in one_lineup]
print names
