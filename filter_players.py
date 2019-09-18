import pandas as pd
from constants import CONTEST_ID as cid
from constants import TEAMS_NF_FD

#pool_file = "-".join(['FanDuel-NFL', cid, 'players-list.csv'])
pool_file = "-".join(['FanDuel-NFL', cid, 'owned.csv'])
pool = pd.read_csv('data/pool/' + pool_file)
df = pd.read_csv('data/nf_projections.csv')

# modify team names to match player pool
df['team'] = df['team'].str.upper()
df = df.replace({'team': TEAMS_NF_FD})

# get eligible teams from player pool
teams_elg = pool['Team'].unique()

# from projections, remove players not on eligible teams
df = df[df['team'].isin(teams_elg)]

df.to_csv('data/projections_eligible.csv', index=False)
