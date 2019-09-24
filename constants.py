N_LINEUPS = 20

YEAR = 2019

ROSTER = {'qb': 1,
          'rb': 2,
          'wr': 3,
          'flex': 1,
          'te': 1,
          'dst': 1}

# roster budget for contest
BUDGET = 60000

# contest identifier
CONTEST_ID = '2019-09-22-38567'

TEAMS_NF_FD = {'WSH': 'WAS',
               'LA': 'LAR'
               }

MIN_UNIQUE = 3

MAX_OVERLAP = sum(ROSTER.values()) - MIN_UNIQUE

MAX_EXPOSURE = {'QB': 0.25, 
                'RB': 0.35, 
                'WR': 0.30,
                'TE': 0.30,
                'DST': 0.25}
