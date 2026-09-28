# pull_data.py
# Pulls NBA team game logs from the NBA stats API and saves them to data/raw_games.csv
# Run this from YOUR computer (home wifi), not Colab. stats.nba.com blocks Colab's servers, which is why it kept timing out.
#
# Usage (from the project folder):  python pull_data.py

import os
import time
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder

# 2019-20 through 2024-25 (six seasons)
SEASONS = ['2019-20', '2020-21', '2021-22', '2022-23', '2023-24', '2024-25']
MAX_ATTEMPTS = 4


def pull_season(season):
    """Pull one season of regular season team games, retrying if the API times out."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            print(f"Pulling {season} (attempt {attempt})...")
            finder = leaguegamefinder.LeagueGameFinder(
                season_nullable=season,
                season_type_nullable='Regular Season',  # regular season only, so no preseason/playoff games sneak in
                league_id_nullable='00',                # '00' = NBA only
                timeout=60,
            )
            games = finder.get_data_frames()[0]
            print(f"  got {len(games)} rows")
            return games
        except Exception as e:
            print(f"  attempt {attempt} failed: {e}")
            time.sleep(5 * attempt)  # wait a little longer after each failure
    raise RuntimeError(f"Could not pull {season} after {MAX_ATTEMPTS} attempts")


def main():
    all_games = []
    for season in SEASONS:
        all_games.append(pull_season(season))
        time.sleep(2)  # be polite to the API between seasons

    df = pd.concat(all_games, ignore_index=True)

    os.makedirs('data', exist_ok=True)
    df.to_csv('data/raw_games.csv', index=False)
    print(f"\nDone. Saved {len(df)} rows and {df.shape[1]} columns to data/raw_games.csv")


if __name__ == '__main__':
    main()
