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
    match_date TEXT NOT NULL,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    home_score INTEGER,
    away_score INTEGER
);
