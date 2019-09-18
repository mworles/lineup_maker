import pandas as pd
import numpy as np
from constants import CONTEST_ID as cid
from fuzzywuzzy import process
from fuzzywuzzy import fuzz


#pool_file = "-".join(['FanDuel-NFL', cid, 'players-list.csv'])
pool_file = "-".join(['FanDuel-NFL', cid, 'owned.csv'])
pool = pd.read_csv('data/pool/' + pool_file)
df = pd.read_csv('data/projections_eligible.csv')

# changes to player pool names for name matching
pool['Nickname'] = pool['Nickname'].str.lower()
ids = pool.set_index('Id')
pool = pool.set_index('Nickname')


def get_id(row):
    team = row['team']
    name = row['name']
    pool_team = pool.loc[pool['Team'] == team]
    if 'd/st' not in name:
        name_len = len(name.split(' '))
        if name in pool_team.index:
            pool_id = pool_team.loc[name]['Id']
            return pool_id
        else:
            pool_team_players = pool_team.index.values
            best_match = process.extractOne(name, pool_team_players)
            if best_match[1] > 80:
                pool_id = pool.loc[best_match[0], 'Id']
                return pool_id
            else:
                return 'NA'
    else:
        crit = (pool['Team'] == team) & (pool['Position'] == 'D')
        pool_id = pool.loc[crit, 'Id'].values[0]
        return pool_id

df['pool_id'] = df.apply(lambda x: get_id(x), axis=1)

na_crit = df['pool_id'] == 'NA'
na_len = df[na_crit].shape[0]
print '%s projected players with no pool id' % (na_len)
print df[df['pool_id'] == 'NA']['name'].values

df.to_csv('data/pool.csv', index=False)

mrg = pd.merge(df, pool, left_on='pool_id', right_on='Id',
               how='inner')
mrg.to_csv('data/pool_owned.csv', index=False)
