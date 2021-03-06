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
    use_match INTEGER DEFAULT 0,  -- Boolean (1 or 0)
    home_score INTEGER,
    away_score INTEGER,
    game_number INTEGER
);

CREATE TABLE PLAYERS (
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    join_date TEXT NOT NULL,
    retired INTEGER DEFAULT 0
);

CREATE TABLE ROUNDS_NEW (
    id INTEGER PRIMARY KEY,
    start_date TEXT NOT NULL,
    end_date TEXT,
    buy_in_pence INTEGER NOT NULL  -- Player buy in (pence)
);

CREATE TABLE ROUND_WINNERS (
    round_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL
)

CREATE TABLE PREDICTIONS (
    id INTEGER PRIMARY KEY,
    round_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    match_id INTEGER NOT NULL,
    prediction TEXT NOT NULL,
    [drop] INTEGER DEFAULT 0
);

CREATE TABLE TEAM_XREF (
    team_name TEXT NOT NULL,
    xref TEXT NOT NULL
);

CREATE TABLE PLAYER_XREF (
    player_name TEXT NOT NULL,
    xref TEXT NOT NULL
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
LEFT JOIN [ROUNDS] AS [r] ON [s].[round_id] = [r].[id]
WHERE [r].[winner_id] IS NULL  -- remove this and get grouping right for comparing past and present rounds
ORDER BY [s].[match_date];

CREATE VIEW CURRENT_ROUND AS
SELECT
    [r].[id] AS [round_id],
    [r].[start_date] AS [start_date],
    [d].[current_match_date] AS [current_match_date],
    [d].[matches] AS [matches],
    (SELECT COUNT([id]) FROM [PLAYERS]) AS [players],
    ([r].[buy_in_pence] * [d].[matches] * (SELECT COUNT([id]) FROM [PLAYERS])) AS [jackpot]
FROM [ROUNDS] AS [r]
LEFT JOIN (
    SELECT
        [r].[id] AS [id],
        MAX([m].[match_date]) AS [current_match_date],
        COUNT(DISTINCT strftime('%Y%m%d', [m].[match_date])) AS [matches]
    FROM [MATCHES] AS [m]
    INNER JOIN [ROUNDS] AS [r] ON [m].[match_date] >= [r].[start_date]
    WHERE [m].[use_match] = 1
    GROUP BY [r].[id]
) AS [d] ON [r].[id] = [d].[id]
WHERE [r].[winner_id] IS NULL;

CREATE VIEW GAMEWEEKS AS
SELECT
    DISTINCT [m].[match_date] AS [match_date]
FROM [MATCHES] AS [m]
INNER JOIN [ROUNDS] AS [r] ON [m].[match_date] >= [r].[start_date]
WHERE [r].[winner_id] IS NULL
AND [m].[use_match] = 1
ORDER BY [m].[match_date];

CREATE VIEW MAX_PLAYER_ID AS
SELECT
    MAX([id]) AS [id]
FROM [players];
