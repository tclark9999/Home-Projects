import pandas as pd
import requests
from bs4 import BeautifulSoup, Comment
import re
import time
import string
import os



def get_player_urls(f_url,letter):
    time.sleep(3.5)

    #Get the html for the team
    roster_page = requests.get(f_url)
    #Use Beautiful Soup on the HTML content
    roster_soup = BeautifulSoup(roster_page.content,"html.parser")
    
    # #find all the links for the players and assemble the link to that player's game log
    player_elements = roster_soup.find_all("a")
    base_url = 'https://www.pro-football-reference.com'
    player_list =  [base_url + player["href"].replace('.htm','') + '/gamelog/' for player in player_elements if f'players/{letter}/' in player["href"]]
    return player_list


def get_player_data_frame(play_url):
    #Pull HTML tables into pandas
    player_all_df = pd.read_html(play_url)
    #Use First Table (Regular Season)
    player_df = player_all_df[0]
    #Combine Mult-Layer column names
    player_df.columns = [f'{i}|{j}' if 'Unnamed' not in str(i) else f'{j}' for i,j in player_df.columns]

    #Get html for player page to get player info
    player_page = requests.get(play_url)
    #Use Beautiful soup on the html
    player_soup = BeautifulSoup(player_page.content,'html.parser')
    #Find id meta for player info
    player_meta = player_soup.find(id="meta")
    #Get just the text
    player_desc =  player_meta.get_text()
    #Regex search for the player position
    player_position = re.search('Position:(.*)',player_desc).group(1)
    #Set player position column
    player_df['Position'] = player_position
    player_df['Bio'] = player_desc
    player_id = play_url.split('/')[-3].split('.')[0]
    #Get just the text for the player name for file
    player_name = player_soup.h1.span.get_text()
    
    player_df['Player Name'] = player_name

    return player_df, player_position,player_id



if __name__ == "__main__":
    url = 'https://www.pro-football-reference.com/players/'

    alph = (string.ascii_uppercase)

    players =[get_player_urls(url + a + '/',a) for a in alph]

    base_path = fr'C:\Users\Tyler\OneDrive\Documents\Fantasy Data'

    time.sleep(5)

    for i in range(len(players)):
        print(alph[i])
        player_list = players[i]

        for player in player_list:
            time.sleep(3.5)
            try:
                player_data, player_pos, player_id = get_player_data_frame(player)

                player_pos = player_pos.strip()

                newpath = fr'{base_path}\{player_pos}'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)

                player_data.to_csv(fr"{newpath}\{player_id}.csv")
            except:
                pass

