import requests
from bs4 import BeautifulSoup
import pandas as pd
import psycopg2
from datetime import date
import boto3
import io 
import csv

def lambda_handler(event, context):
    def scrape_and_prepare_df(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/120.0.0.0 Safari/537.36'
        }
        #Webscraping from espn
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        jobs = soup.find_all('div', class_='ResponsiveTable Table__league-injuries')
        #These arrays will be used to handle attributes in df(player, date, position, status, comment, team, etc.)
        playerlist, returndatelist, positionlist, statuslist, commentlist, teamlist = [], [], [], [], [], []
        #increments attributes through for loop, adds to arrays above
        for job in jobs:
            finaltext = job.find_all('a', class_='AnchorLink')
            positiontext = job.find_all('td', class_='col-pos Table__TD')
            returndatetext = job.find_all('td', class_='col-date Table__TD')
            statustext = job.select('span.TextStatus.TextStatus--red.plain, span.TextStatus.TextStatus--yellow.plain')
            commenttext = job.find_all('td', class_='col-desc Table__TD')
            teamfinaltext = job.find_all('span', class_='injuries__teamName ml2')
        
            title_texts = [i.get_text() for i in finaltext]
            team_texts = [j.get_text() for j in teamfinaltext]

            playerlist += title_texts
            positionlist += [i.get_text() for i in positiontext]
            returndatelist += [i.get_text() for i in returndatetext]
            statuslist += [i.get_text() for i in statustext]
            commentlist += [i.get_text() for i in commenttext]
            teamlist += [team_texts[0] if team_texts else ""] * len(title_texts)

        max_len = max(len(playerlist), len(positionlist), len(returndatelist), len(statuslist), len(teamlist), len(commentlist))

        def pad_list(lst, target_len, filler=""):
            return lst + [filler] * (target_len - len(lst))

        playerlist     = pad_list(playerlist, max_len)
        positionlist   = pad_list(positionlist, max_len)
        returndatelist = pad_list(returndatelist, max_len)
        statuslist     = pad_list(statuslist, max_len)
        teamlist       = pad_list(teamlist, max_len)
        commentlist    = pad_list(commentlist, max_len)
        #declares df to handle information
        df = pd.DataFrame({
            "Player": playerlist,
            "Position": positionlist,
            "Date of Injury": returndatelist,
            "Current Date": pd.to_datetime(date.today()),
            "Status": statuslist,
            "Team": teamlist,
            "Injury": commentlist
        })
        #functions to handle edge cases where the season overlaps different years
        def convert_date(num):
            if num.startswith('Jan'): num = num.replace('Jan', '01')
            elif num.startswith('Feb'): num = num.replace('Feb', '02')
            elif num.startswith('Mar'): num = num.replace('Mar', '03')
            elif num.startswith('Apr'): num = num.replace('Apr', '04')
            elif num.startswith('May'): num = num.replace('May', '05')
            elif num.startswith('Jun'): num = num.replace('Jun', '06')
            elif num.startswith('Jul'): num = num.replace('Jul', '07')
            elif num.startswith('Aug'): num = num.replace('Aug', '08')
            elif num.startswith('Sep'): num = num.replace('Sep', '09')
            elif num.startswith('Oct'): num = num.replace('Oct', '10')
            elif num.startswith('Nov'): num = num.replace('Nov', '11')
            else: num = num.replace('Dec', '12')
            return ('2025 ' + num).replace(' ', '-')
        #function to polish date strcuture and convert from date to datetime object
        def convert_date_pt2(num):
            if len(num) == 9 and num[-2] == '-':
                num = num[:-1] + '0' + num[-1]
            return num
        
        df['Date of Injury'] = df['Date of Injury'].apply(convert_date).apply(convert_date_pt2)
        df["Date of Injury"] = pd.to_datetime(df["Date of Injury"], format="%Y-%m-%d")
        #converts diffrent injuries listed found in body_parts array to body part affected in table
        def extract_body_parts(injury_desc):
            body_parts = ['hand', 'arm', 'shoulder', 'knee', 'Achilles', 'labrum', 'hamstring',
                          'ankle', 'foot', 'thumb', 'wrist', 'rest', 'adductor', 'hip', 'acl',
                          'pelvis', 'groin', 'elbow', 'calf', 'back', 'toe', 'concussion', 'illness', 'quadriceps']
            final_injury = []
            for part in body_parts:
                if part.lower() in injury_desc.lower():
                    final_injury.append('ankle' if part == 'Achilles' else 'shoulder' if part == 'labrum' else part)
            return ', '.join(set(final_injury))

        df['Body Parts Affected'] = df['Injury'].apply(extract_body_parts)
        return df
    #Connect to RDS
    try:
        conn = psycopg2.connect(
            host="de-tables.co5wi6mwqtgt.us-east-1.rds.amazonaws.com",
            database="sportsinjurydb",
            user="adarisi7",
            password="123#Master",
            port=5432
        )
        cur = conn.cursor()
        #Have 3 tables in RDS, sports that just has sport id with sport, players for each unique player injured, and injury for each unique injury
        sports_df = pd.read_sql("SELECT * FROM sports", conn)
        players_df = pd.read_sql("SELECT * FROM players", conn)
        injuries_df = pd.read_sql("SELECT * FROM injuries", conn)
        #This function is called for webscraping the certain website based on sport(basketball->espn NBA, football-> espn NFL etc.)
        all_dfs = [
            ("Basketball", scrape_and_prepare_df("https://www.espn.com/nba/injuries")),
            ("Football", scrape_and_prepare_df("https://www.espn.com/nfl/injuries")),
            ("Baseball", scrape_and_prepare_df("https://www.espn.com/mlb/injuries")),
            ("Hockey", scrape_and_prepare_df("https://www.espn.com/nhl/injuries"))
        ]
        
        for sport_name, df in all_dfs:
            result_df = pd.read_sql(f"SELECT s.sport_id FROM sports as s WHERE s.sport = '{sport_name}'", conn)
            sport_id_value = result_df.iloc[0, 0]
            #create a temp player for new unique players picked up on current run
            temp_players = pd.DataFrame({
                "player_name": df["Player"],
                "player_position": df["Position"],
                "team": df["Team"],
                "sport_id": sport_id_value
            })
            #We then add it to the players table and drop duplicates, keepin first occurence 
            #Then reset index to maintain correct structure of table
            temp_players = temp_players.drop_duplicates(subset=['player_name'], keep='first')
            temp_players.reset_index(drop=True, inplace=True)
            temp_players["player_id"] = range(1, len(temp_players) + 1)

            players_df = pd.concat([players_df, temp_players], ignore_index=True)
            players_df = players_df.drop_duplicates(subset=['player_name'], keep='first')
            players_df.reset_index(drop=True, inplace=True)
            players_df["player_id"] = range(1, len(players_df) + 1)
            #Add temp injuries table for injuries picked up in current run
            temp_injuries_df = pd.DataFrame({
                'injury_description': df["Injury"],
                'body_part': df["Body Parts Affected"],
                'status': df["Status"],
                'date_of_injury': df["Date of Injury"],
                'today_date': df["Current Date"],
                'player_name': df["Player"],
                'sports_injury_id': sport_id_value
            })
            ## Merge injuries with player_id using player_name to link; ensures each injury is associated with a valid player
            temp_injuries_merged = temp_injuries_df.merge(players_df[['player_id', 'player_name']], on='player_name', how='left')
            injuries_df = pd.concat([injuries_df, temp_injuries_merged], ignore_index=True)
        ## Fetch existing injuries to avoid re-inserting duplicates (defined as same player, date, and status)
        existing_injuries = pd.read_sql("SELECT player_id, date_of_injury, status FROM injuries", conn)
        # Keep only those injuries that are not already present in the database (i.e., truly new records)
        injuries_df_filtered = injuries_df.merge(
            existing_injuries,
            on=['player_id', 'date_of_injury', 'status'],
            how='left',
            indicator=True
        ).query("_merge == 'left_only'").drop(columns=['_merge'])

        # Reset index to keep clean DataFrame after filtering
        injuries_df_filtered = injuries_df_filtered.reset_index(drop=True)

        # Determine the next available injury_id by getting the max current ID (or 0 if table is empty)
        cur.execute("SELECT COALESCE(MAX(injury_id), 0) FROM injuries")
        max_existing_id = cur.fetchone()[0]
        # Assign new unique injury IDs starting from the next available number
        injuries_df_filtered["injury_id"] = range(max_existing_id + 1, max_existing_id + 1 + len(injuries_df_filtered))
        # Pull full injuries table to prepare updated full dataset for S3 push
        # Reset index similiar to players table
        existing_injuries_push = pd.read_sql("SELECT * FROM injuries", conn)
        injuries_df_push = pd.concat([existing_injuries_push, injuries_df_filtered], ignore_index=True)
        injuries_df_push.reset_index(drop=True, inplace=True)
        injuries_df_push["injury_id"] = range(1, len(injuries_df_push) + 1)

        # Ensure ID fields are cast to integer type to avoid type issues during DB insert or S3 export
        for col in ['injury_id', 'player_id', 'sports_injury_id']:
            injuries_df_push[col] = injuries_df_push[col].astype(int)

        # Identify players that are new by checking for absence of their player_id in the current players table
        existing_players = pd.read_sql("SELECT player_id FROM players", conn)["player_id"]
        players_df_filtered = players_df[~players_df["player_id"].isin(existing_players)]

        # Insert new players into the players table only if any were found
        if not players_df_filtered.empty:
            insert_query_players = """
                INSERT INTO players (player_id, player_name, player_position, team, sport_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            player_values = players_df_filtered[
                ["player_id", "player_name", "player_position", "team", "sport_id"]
            ].values.tolist()
            cur.executemany(insert_query_players, player_values)

        # Insert new injuries into the injuries table only if any new rows were found
        if not injuries_df_filtered.empty:
            insert_query_injuries = """
                INSERT INTO injuries (
                    injury_id, injury_description, body_part, status,
                    date_of_injury, today_date, player_id, sports_injury_id, player_name
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            injury_values = injuries_df_filtered[
                ["injury_id", "injury_description", "body_part", "status",
                 "date_of_injury", "today_date", "player_id", "sports_injury_id", "player_name"]
            ].values.tolist()
            cur.executemany(insert_query_injuries, injury_values)

        conn.commit()
        #setS3 to take file by current date 
        today_str = date.today().strftime('%Y-%m-%d')
        s3 = boto3.client('s3')

        # Upload injuries
        buffer1 = io.StringIO()
        injuries_df_push.to_csv(buffer1, index=False, quoting=csv.QUOTE_NONNUMERIC)
        s3.put_object(
            Bucket='daily-injury-storage',
            Key=f'injuries/injuries_{today_str}.csv',
            Body=buffer1.getvalue()
        )

        # Upload playerss3
        buffer2 = io.StringIO()
        players_df.to_csv(buffer2, index=False)
        s3.put_object(
            Bucket='daily-injury-storage',
            Key=f'players/players_{today_str}.csv',
            Body=buffer2.getvalue()
        )

        cur.close()
        return {
            "status": "Success",
            "players_added": len(players_df_filtered),
            "injuries_added": len(injuries_df_filtered)
        }

    except Exception as e:
        return {"error": str(e)}
