import pandas as pd
import numpy as np
import cvxpy
import random
import operator
from constants import ROSTER, BUDGET, CONTEST_ID
from constants import N_LINEUPS, MAX_OVERLAP, MAX_EXPOSURE
from cleaning import get_relative_points, clean_names


def get_constraints(n_todraft, roster_todraft, player_pool, budget, selection,
                    costs, team_limit = False):
            
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
    
    # constraint 11: set a minimun salary constraint
    # expect entries to use all or nearly all of the budget
    con_budget_min = costs * selection >= (budget - 800)
    constraints.append(con_budget_min)
    
    if team_limit == True:
        all_teams = player_pool['team'].unique()
        for team in all_teams:
            ta = np.array(player_pool['team'] == team).astype(int)
            con_ta = ta * selection <= 3
            constraints.append(con_ta)
    
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
week = 1
year = 2017

df = get_relative_points(year, week)
df = clean_names(df)

# set budget
budget = BUDGET
roster_todraft = ROSTER
n_start = sum(ROSTER.values())
lineups_toget = N_LINEUPS
lineups_got = 0

# name column to sum for the maximization function 
rtn = 'Points'

lineups = []
lineups_sets = []


#def randomize_pool(df):
    


while lineups_got < lineups_toget:

    # copy of cheatsheet data to update during nomination
    player_pool = df.copy()
    
    costs = np.array(player_pool.loc[:, 'sal']).astype(int)
    selection = cvxpy.Bool(len(costs))
    
    new_lineup = False
    
    while new_lineup == False:

        # get indices of players to select
        constraints = get_constraints(n_start, roster_todraft,
                                      player_pool, budget, selection,
                                      costs, team_limit=False)
        sel_index = get_selection_indices(player_pool, selection,
                                          constraints, n_start)
        lineup = player_pool.iloc[sel_index, :].sort_values('pos')
        lineup_ids = lineup.index.values
        
        if set(lineup_ids) in lineups_sets:
            print 'duplicate lineup, removing id'
            id_remove = random.choice(lineup_ids)
            player_pool = player_pool.drop(id_remove)
            costs = np.array(player_pool.loc[:, 'sal']).astype(int)
            selection = cvxpy.Bool(len(costs))    
        else:
            new_lineup = True
    
    print "Lineup %s" % (lineups_got + 1)
    print ''
    print lineup
    print lineup['Points'].sum(), lineup['sal'].sum()
    lineups.append(lineup_ids)
    lineups_sets.append(set(lineup_ids))
    lineups_got += 1
"""
cols_tmp = ['QB', 'RB', 'RB', 'WR', 'WR', 'WR', 'TE', 'FLEX', 'DEF']
df_tmp = pd.DataFrame(lineups, columns = cols_tmp)
f_tmp = "".join(['FanDuel-NFL-', CONTEST_ID, '-lineup-upload-template.csv'])
df_tmp.to_csv('output/' + f_tmp, index=False)

sorted_used = sorted(id_prop.items(), key=operator.itemgetter(1), reverse=True)

name_dict = df[['pool_id', 'name']].set_index('pool_id').to_dict('index')

for id_prop in sorted_used:
    id = id_prop[0]
    print name_dict[id]['name'], round(id_prop[1], 2)

lineup_names = [[get_name(p, name_dict) for p in l] for l in lineups]

df_names = pd.DataFrame(lineup_names, columns=cols_tmp)
f_names = "".join(['FanDuel-NFL-', CONTEST_ID, '-lineup_names.csv'])
df_names.to_csv('output/' + f_names, index=False)
"""
