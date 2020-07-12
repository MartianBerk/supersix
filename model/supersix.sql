/*
 * SQLite Table for Super Six Game.
 */

 CREATE TABLE LEAGUES (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    code TEXT,
    start_date TEXT,
    current_matchday INTEGER
);

 CREATE TABLE MATCHES (
    id INTEGER PRIMARY KEY,
    league_id INTEGER NOT NULL,
    matchday INTEGER NOT NULL,
    match_date TEXT NOT NULL,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    home_score INTEGER,
    away_score INTEGER
);

CREATE TABLE PLAYERS (
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    join_date TEXT NOT NULL
);

CREATE TABLE ROUNDS (
    id INTEGER PRIMARY KEY,
    start_date TEXT NOT NULL,
    end_date TEXT,
    buy_in_pence INTEGER NOT NULL,  -- Player buy in (pence)
    winner_id INTEGER
);

CREATE TABLE PREDICTIONS (
    id INTEGER PRIMARY KEY,
    round_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    match_id INTEGER NOT NULL,
    prediction TEXT NOT NULL
);
