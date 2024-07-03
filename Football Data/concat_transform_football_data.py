import pandas as pd
import os
import glob
import numpy as np


def set_fantasy_position(position):
    if position in ('WR/RB', 'WR-RB'):
        return 'WR-RB'
    elif 'QB' in position:
        return 'QB'
    elif 'WR' in position:
        return 'WR'
    elif 'TE' in position:
        return 'TE'
    elif 'RB' in position:
        return 'RB'
    elif 'K' in position:
        return 'K'
    else :
        return "Other"

def concat_player_data(base_path):

    # Use os.walk to traverse through the directory structure starting from the base path
    list_dir = os.walk(base_path)

    # Initialize an empty list to store file paths
    files = []

    # Iterate through the directory structure
    for root, dirs, dir_files in list_dir:
        # For each file in the current directory, check if "2022" is not in the directory path
        # If not, create a tuple containing the complete file path and the file name, and add it to the files list
        files += [(root + "\\" + f, f) for f in dir_files if "2022" not in root]

    # Initialize an empty list to store DataFrames
    player_list = []

    # Iterate through the list of file tuples
    for f in files:
        # Read the CSV file into a DataFrame
        ply_df = pd.read_csv(f[0])
        # Extract the player ID from the file name and add it as a new column "player_id" in the DataFrame
        ply_df['player_id'] = f[1].replace('.csv', '')
        # Append the DataFrame with player data to the player_list
        player_list.append(ply_df)

    # Concatenate all DataFrames in the player_list into a single DataFrame
    player_df = pd.concat(player_list)

    player_df = player_df.reset_index()

    return player_df



def transform_player_data_to_fantasy(player_df):
    player_df = player_df[(player_df['Age'].notnull()) & (player_df['Age'] != 'Age')]

    player_df =   player_df.rename(columns={'Unnamed: 7_level_1':'Home_Away'})
    player_df['Home_Away'] = player_df['Home_Away'].replace('@','Away').fillna('Home')

    player_df = player_df[~player_df['Year'].isna()]
    player_df['Year'] = player_df['Year'].astype(float).astype(int)
    player_df = player_df[player_df['Year'] >= 2003]

    player_df = player_df[player_df['Position'].str.contains('|'.join(['WR','QB','TE','RB','K']))]
    

    player_df['Off. Snaps Float'] = player_df['Off. Snaps|Pct'].str.replace("%","").astype(float)
    player_df['Off. Snaps Rate'] = player_df['Off. Snaps Float'].values/100

    player_df['Receiving Ctch Float'] = player_df['Receiving|Ctch%'].str.replace("%","").astype(float)
    player_df['Receiving Ctch Rate'] = player_df["Receiving Ctch Float"].values/100

    player_df['fantasy_points'] = (player_df["Rushing|Yds"].fillna(0).astype(float).values/10.0) + \
                (player_df["Receiving|Yds"].fillna(0).astype(float).values/10.0) + player_df["Receiving|Rec"].fillna(0).astype(float).values \
                + (player_df["Rushing|TD"].fillna(0).astype(float).values * 6.0) + (player_df['Receiving|TD'].fillna(0).astype(float).values * 6.0)\
                + (player_df["Kick Returns|Yds"].fillna(0).astype(float).values/10) + (player_df['Kick Returns|TD'].fillna(0).astype(float).values * 6.0)\
                + (player_df["Punt Returns|Yds"].fillna(0).astype(float).values/10) + (player_df['Punt Returns|TD'].fillna(0).astype(float).values * 6.0)\
                + (player_df["Scoring|2PM"].fillna(0).astype(float).values * 2.0) + (player_df["Passing|Int"].fillna(0).astype(float).values * -1.0)\
                + (player_df["Fumbles|FL"].fillna(0).astype(float).values * -2.0) + (player_df["Passing|Yds"].fillna(0).astype(float).values/25)\
                + (player_df["Passing|TD"].fillna(0).astype(float).values * 6.0)

    

    player_df['Year_of_service'] = player_df.groupby('player_id')['Year'].rank(method='dense')    

    player_df['Position'] = player_df['Position'].str.strip()

    player_df['fantasy_position'] = player_df['Position'].apply(lambda x: set_fantasy_position(x))

    player_df['total_yards'] = (player_df['Rushing|Yds'].fillna(0).astype(np.float16) 
                + player_df['Receiving|Yds'].fillna(0).astype(np.float16) + player_df['Kick Returns|Yds'].fillna(0).astype(float) 
                + player_df['Punt Returns|Yds'].fillna(0).astype(float) 
                )
    
    player_df['age_int'] = player_df['Age'].astype(float).astype(int)
    
    player_df = player_df.replace('Inactive',np.nan)

    player_df = player_df.fillna(0)

    return player_df


def fantasy_agg_year_data(player_fantasy_df):
    player_fantasy_df = player_fantasy_df[['Rk', 'Year', 'Date', 'G#', 'Week', 'Age', 'Tm',
        'Home_Away', 'Opp', 'Result', 'GS', 'Rushing|Att',
        'Rushing|Yds', 'Rushing|Y/A', 'Rushing|TD', 'Receiving|Tgt',
        'Receiving|Rec', 'Receiving|Yds', 'Receiving|Y/R', 'Receiving|TD',
        'Receiving|Ctch%', 'Receiving|Y/Tgt', 'Kick Returns|Rt',
        'Kick Returns|Yds', 'Kick Returns|Y/Rt', 'Kick Returns|TD',
        'Scoring|2PM', 'Scoring|TD', 'Scoring|Pts', 'Fumbles|Fmb', 'Fumbles|FL',
        'Fumbles|FF', 'Fumbles|FR', 'Fumbles|Yds', 'Fumbles|TD',
        'Off. Snaps|Num', 'Off. Snaps|Pct',
        'ST Snaps|Num', 'ST Snaps|Pct', 'Status', 'Position', 'Player Name',
        'Sk','Passing|Cmp', 'Passing|Att', 'Passing|Cmp%',
        'Passing|Yds', 'Passing|TD', 'Passing|Int', 'Passing|Rate',
        'Passing|Sk', 'Passing|Yds.1', 'Passing|Y/A', 'Passing|AY/A',
        'Punt Returns|Ret', 'Punt Returns|Yds', 'Punt Returns|Y/R',
        'Punt Returns|TD','player_id','Year_of_service','fantasy_points',
        'Off. Snaps Rate', 'Receiving Ctch Rate',"fantasy_position", "total_yards","age_int"]]
    
    player_fantasy_df['Off. Snaps Total'] =  player_fantasy_df['Off. Snaps|Num'].fillna(0).values / player_fantasy_df['Off. Snaps Rate'].fillna(0).values 
    player_fantasy_df['Off. Snaps Total'] = player_fantasy_df['Off. Snaps Total'].fillna(0).astype(int)

    agg_dict = {
    'Rushing|Att': 'sum', 'Rushing|Yds': 'sum','Rushing|TD':'sum','Receiving|Tgt':'sum', 'Receiving|Rec':'sum', 
    'Receiving|Yds':'sum', 'Receiving|TD':'sum', 'Kick Returns|Rt':'sum', 'Kick Returns|Yds':'sum', 'Kick Returns|TD':'sum', 
    'Scoring|2PM':'sum', 'Scoring|TD':'sum', 'Scoring|Pts':'sum', 'Fumbles|Fmb':'sum', 'Fumbles|FL':'sum',
    'Off. Snaps|Num':'sum', 'ST Snaps|Num':'sum', 'Passing|Cmp':'sum', 'Passing|Att':'sum', 'Passing|Yds':'sum',
     'Passing|TD':'sum', 'Passing|Int':'sum', 'Passing|Sk':'sum', 'Punt Returns|Ret':'sum', 'Punt Returns|Yds':'sum','Punt Returns|TD':'sum',
     'Year_of_service':'min','fantasy_points':'sum','age_int':'min','total_yards':'sum','Off. Snaps Total':'sum'
    }

    player_fantasy_year = player_fantasy_df[['Year','player_id','fantasy_position','Player Name','Rushing|Att',
                'Rushing|Yds','Rushing|TD','Receiving|Tgt', 'Receiving|Rec', 'Receiving|Yds', 'Receiving|TD',
                'Kick Returns|Rt', 'Kick Returns|Yds', 'Kick Returns|TD', 'Scoring|2PM', 'Scoring|TD', 'Scoring|Pts',
                'Fumbles|Fmb', 'Fumbles|FL','Off. Snaps|Num', 'ST Snaps|Num', 'Passing|Cmp', 'Passing|Att', 'Passing|Yds',
                'Passing|TD', 'Passing|Int', 'Passing|Sk', 'Punt Returns|Ret', 'Punt Returns|Yds','Punt Returns|TD',
                'Year_of_service','fantasy_points','age_int'
                ,'total_yards','Off. Snaps Total']].groupby(['Year','player_id',
                                                    'fantasy_position','Player Name'], as_index=False).agg(agg_dict)
    
    player_fantasy_year['rush_yrd_att'] = player_fantasy_year['Rushing|Yds'].values/player_fantasy_year['Rushing|Att'].values
    player_fantasy_year['rec_yrd_rec'] = player_fantasy_year['Receiving|Yds'].values/player_fantasy_year['Receiving|Rec'].values
    player_fantasy_year['rec_yrd_tgt'] = player_fantasy_year['Receiving|Yds'].values/player_fantasy_year['Receiving|Tgt'].values
    player_fantasy_year['rec_ctch_rate'] = player_fantasy_year['Receiving|Rec'].values/player_fantasy_year['Receiving|Tgt'].values
    player_fantasy_year['off_snap_rate'] = player_fantasy_year['Off. Snaps|Num'].values/player_fantasy_year['Off. Snaps Total'].values
    player_fantasy_year['rec_rush_tot'] = player_fantasy_year['Rushing|Att'].values + player_fantasy_year['Receiving|Rec'].values
    player_fantasy_year['fum_rate'] = player_fantasy_year['Fumbles|Fmb']/player_fantasy_year['rec_rush_tot']
    player_fantasy_year['pass_comp_rate'] = player_fantasy_year['Passing|Cmp'].values/player_fantasy_year['Passing|Att'].values
    player_fantasy_year['pass_yrd_comp'] = player_fantasy_year['Passing|Yds'].values/player_fantasy_year['Passing|Cmp'].values
    player_fantasy_year['pass_sk_rate'] = player_fantasy_year['Passing|Sk'].values/player_fantasy_year['Passing|Att'].values
    player_fantasy_year['kick_yrd_ret'] = player_fantasy_year['Kick Returns|Yds'].values/player_fantasy_year['Kick Returns|Rt'].values
    player_fantasy_year['punt_yrd_ret'] = player_fantasy_year['Punt Returns|Yds'].values/player_fantasy_year['Punt Returns|Ret'].values
    player_fantasy_year = player_fantasy_year.replace([np.inf, -np.inf], 0).fillna(0)

    return player_fantasy_year


if __name__ == "__main__":

    base_path = "C:\\Users\\Tyler\\OneDrive\\Documents\\Fantasy Data\\"

    all_player_data = concat_player_data(base_path=base_path)

    all_player_data.to_csv("C:\\Users\\Tyler\\OneDrive\\Documents\\Concatenated Fantasy Data\\all_players.csv")

    fantasy_data = transform_player_data_to_fantasy(all_player_data)

    fantasy_data.to_csv("C:\\Users\\Tyler\\OneDrive\\Documents\\Concatenated Fantasy Data\\fantasy_data.csv")

    fantasy_year_data =  fantasy_agg_year_data(fantasy_data)

    fantasy_year_data.to_csv("C:\\Users\\Tyler\\OneDrive\\Documents\\Concatenated Fantasy Data\\fantasy_year_data.csv")