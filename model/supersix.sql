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
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT NOT NULL,
    league_id INTEGER NOT NULL,
    matchday INTEGER NOT NULL,
    match_date TEXT NOT NULL,
    match_minute INTEGER,
    status TEXT NOT NULL,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    use_match INTEGER,  -- Boolean (1 or 0)
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
    prediction TEXT NOT NULL,
    [drop] INTEGER
);

CREATE VIEW PLAYER_STATS AS
SELECT
    [pr].[round_id] AS [round],
    [pl].[first_name] || ' ' || [pl].[last_name] AS [player],
    strftime('%Y-%m-%d 00:00:00', [m].[match_date]) as [match_date],
    [m].[home_team] AS [home_team],
    [m].[away_team] AS [away_team],
    [pr].[prediction] AS [prediction],
    CASE
        WHEN [pr].[prediction] = 'home' AND [m].[home_score] > [m].[away_score] THEN 1
        WHEN [pr].[prediction] = 'away' AND [m].[away_score] > [m].[home_score] THEN 1
        WHEN [pr].[prediction] = 'draw' AND [m].[home_score] = [m].[away_score] THEN 1
        ELSE 0
    END AS [correct]
FROM [PLAYERS] AS [pl]
INNER JOIN [PREDICTIONS] AS [pr] ON [pl].[id] = [pr].[player_id]
INNER JOIN [MATCHES] AS [m] ON [m].[id] = [pr].[match_id]
WHERE [m].[status] = 'FINISHED'
AND [m].[use_match] = 1
ORDER BY [m].[match_date];

CREATE VIEW PLAYER_STATS_AGG AS
SELECT
    [s].[round_id] AS [round],
    [pl].[first_name] || ' ' || [pl].[last_name] AS [player],
    [s].[match_date] AS [match_date],
    [s].[matches] AS [matches],
    [s].[correct] AS [correct]
FROM [PLAYERS] AS [pl]
INNER JOIN (
    SELECT
        [pr].[round_id] AS [round_id],
        [pr].[player_id] AS [player_id],
        strftime('%Y-%m-%d 00:00:00', [m].[match_date]) AS [match_date],
        COUNT([m].[id]) AS [matches],
        SUM(CASE
                  WHEN [pr].[prediction] = 'home' AND [m].[home_score] > [m].[away_score] THEN 1
                  WHEN [pr].[prediction] = 'away' AND [m].[away_score] > [m].[home_score] THEN 1
                  WHEN [pr].[prediction] = 'draw' AND [m].[home_score] = [m].[away_score] THEN 1
                  ELSE 0
              END
        ) AS [correct]
    FROM MATCHES AS [m]
    INNER JOIN [PREDICTIONS] AS [pr] ON [m].[id] = [pr].[match_id]
    WHERE [m].[status] = 'FINISHED'
    AND [m].[use_match] = 1
    GROUP BY [pr].[round_id], [pr].[player_id], strftime('%Y-%m-%d 00:00:00', [m].[match_date])
) AS [s] ON [s].[player_id] = [pl].[id]
ORDER BY [s].[match_date];

CREATE VIEW CURRENT_ROUND AS
SELECT
    [r].[id] AS [round_id],
    [r].[start_date] AS [start_date],
    [d].[matches] AS [matches],
    [d].[players] AS [players],
    ([r].[buy_in_pence] * [d].[matches] * [d].[players]) AS [jackpot]
FROM [ROUNDS] AS [r]
LEFT JOIN (
    SELECT
        [p].[round_id] AS [id],
        COUNT(DISTINCT strftime('%Y%m%d', [m].[match_date])) AS [matches],
        COUNT(DISTINCT [p].[player_id]) AS [players]
    FROM [PREDICTIONS] AS [p]
    INNER JOIN [MATCHES] AS [m] ON [p].[match_id] = [m].[id]
) AS [d] ON [r].[id] = [d].[id]
WHERE [r].[winner_id] IS NULL;
