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

 CREATE TABLE WORLDCUP_MATCHES (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT NOT NULL,
    league_id INTEGER NOT NULL,
    matchday INTEGER NOT NULL,
    match_date TEXT NOT NULL,
    match_minute INTEGER,
    status TEXT NOT NULL,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    use_match INTEGER DEFAULT 1,  -- Boolean (1 or 0)
    home_score INTEGER,
    away_score INTEGER,
    extra_time INTEGER DEFAULT 0,  -- Boolean (1 or 0)
    penalties INTEGER DEFAULT 0  -- Boolean (1 or 0)
);

CREATE TABLE WORLDCUP_PREDICTIONS (
    id INTEGER PRIMARY KEY,
    player_id INTEGER NOT NULL,
    match_id INTEGER NOT NULL,
    prediction TEXT NOT NULL,
    plus_ninety INTEGER DEFAULT 0,  -- Boolean (1 or 0)
    extra_time INTEGER DEFAULT 0,  -- Boolean (1 or 0)
    penalties INTEGER DEFAULT 0,  -- Boolean (1 or 0)
    [drop] INTEGER DEFAULT 0
);

CREATE TABLE WORLDCUP_PLAYERS (
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL
);

CREATE TABLE PLAYERS (
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    join_date TEXT NOT NULL,
    retired INTEGER DEFAULT 0
);

CREATE TABLE ROUNDS (
    id INTEGER PRIMARY KEY,
    start_date TEXT NOT NULL,
    end_date TEXT,
    buy_in_pence INTEGER NOT NULL  -- Player buy in (pence)
);

CREATE TABLE ROUND_WINNERS (
    round_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL
);

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
    player_name TEXT PRIMARY KEY,
    xref TEXT NOT NULL
);

CREATE TABLE SPECIAL_MESSAGE (
    id INTEGER PRIMARY KEY,
    message TEXT,
    retired INTEGER DEFAULT 0
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
AND [pr].[drop] <> 1
AND [m].[use_match] = 1
ORDER BY [m].[match_date];

CREATE VIEW PLAYER_STATS_AGG AS
SELECT
    [s].[round_id] AS [round],
    [pl].[id] AS [player_id],
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
    WHERE [pr].[drop] <> 1
    AND [m].[status] = 'FINISHED'
    AND [m].[use_match] = 1
    GROUP BY [pr].[round_id], [pr].[player_id], strftime('%Y-%m-%d 00:00:00', [m].[match_date])
) AS [s] ON [s].[player_id] = [pl].[id]
LEFT JOIN [ROUNDS] AS [r] ON [s].[round_id] = [r].[id]
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
    LEFT JOIN (
        SELECT
            [m].[match_date] AS [match_date]
        FROM [MATCHES] AS [m]
        INNER JOIN [ROUNDS] AS [r] ON [m].[match_date] >= [r].[start_date]
        WHERE [r].[end_date] IS NULL
        AND [m].[status] <> 'FINISHED'
        AND [m].[use_match] = 1
        ORDER BY [m].[match_date] DESC
        LIMIT 1
    ) as [ngw]
    WHERE [m].[use_match] = 1
    AND 
    (
        [ngw].[match_date] IS NOT NULL AND [m].[match_date] <= [ngw].[match_date]
        OR
        [ngw].[match_date] IS NULL
    )
    GROUP BY [r].[id]
) AS [d] ON [r].[id] = [d].[id]
WHERE [r].[end_date] IS NULL;

CREATE VIEW GAMEWEEKS AS
SELECT
    DISTINCT [m].[match_date] AS [match_date]
FROM [MATCHES] AS [m]
INNER JOIN [ROUNDS] AS [r] ON [m].[match_date] >= [r].[start_date]
LEFT JOIN (
    SELECT
        [m].[match_date] AS [match_date]
    FROM [MATCHES] AS [m]
    INNER JOIN [ROUNDS] AS [r] ON [m].[match_date] >= [r].[start_date]
    WHERE [r].[end_date] IS NULL
    AND [m].[use_match] = 1
    ORDER BY [m].[match_date] DESC
    LIMIT 1
) as [ngw]
WHERE [r].[end_date] IS NULL
AND [m].[use_match] = 1
AND [m].[match_date] <= [ngw].[match_date]
ORDER BY [m].[match_date];

CREATE VIEW MAX_PLAYER_ID AS
SELECT
    MAX([id]) AS [id]
FROM [players];

CREATE VIEW HISTORIC_ROUNDS AS
SELECT
    [r].[id] AS [round_id],
    [r].[start_date] AS [start_date],
    [r].[end_date] AS [end_date],
    [d].[matches] AS [matches],
    (SELECT COUNT(DISTINCT [player_id]) FROM [PREDICTIONS] WHERE [round_id] = [r].[id]) AS [players],
    ([r].[buy_in_pence] * [d].[matches] * (SELECT COUNT([id]) FROM [PLAYERS])) AS [jackpot],
    [rw].[winner] AS [winner]
FROM [ROUNDS] AS [r]
LEFT JOIN (
    SELECT
        [rw].[round_id] AS [round_id],
        GROUP_CONCAT([p].[first_name] || ' ' || [p].[last_name], ' & ') AS [winner]
    FROM [ROUND_WINNERS] AS [rw]
    LEFT JOIN [PLAYERS] AS [p] ON [rw].[player_id] = [p].[id]
    GROUP BY [rw].[round_id]
) AS [rw] ON [r].[id] = [rw].[round_id]
LEFT JOIN (
    SELECT
        [r].[id] AS [id],
        MAX([m].[match_date]) AS [current_match_date],
        COUNT(DISTINCT strftime('%Y%m%d', [m].[match_date])) AS [matches]
    FROM [MATCHES] AS [m]
    INNER JOIN [ROUNDS] AS [r]
        ON strftime('%Y%m%d', [m].[match_date]) >= strftime('%Y%m%d', [r].[start_date])
        AND strftime('%Y%m%d', [m].[match_date]) <= strftime('%Y%m%d', [r].[end_date])
    WHERE [m].[use_match] = 1
    GROUP BY [r].[id]
) AS [d] ON [r].[id] = [d].[id]
WHERE [r].[end_date] IS NOT NULL;

CREATE VIEW MATCH_PREDICTIONS AS
SELECT
    [r].[id] AS [round_id],
    [pl].[id] AS [player_id],
    [pl].[first_name] AS [first_name],
    [pl].[last_name] AS [last_name],
    [m].[id] AS [match_id],
    [m].[home_team] AS [home_team],
    [m].[away_team] AS [away_team],
    [m].[match_date] AS [match_date],
    [p].[prediction] AS [prediction]
FROM [PREDICTIONS] AS [p]
INNER JOIN [ROUNDS] AS [r] ON [p].[round_id] = [r].[id]
INNER JOIN [PLAYERS] AS [pl] ON [p].[player_id] = [pl].[id]
INNER JOIN [MATCHES] AS [m] ON [p].[match_id] = [m].[id]
WHERE [p].[drop] = 0;

CREATE VIEW LEAGUE_TABLE AS
SELECT
    [t].[league] AS [league],
    [t].[season] AS [season],
    [t].[team] AS [team],
    -- The below only works with SQLITE 3.32 and above (Can't install on server). Have to use this with a season and a league in the WHERE, can then use the order to determine position.
    /*
      RANK () OVER(
        PARTITION BY [league], [season]
        ORDER BY [points] DESC, [goal_difference] DESC
    ) AS [position],
    */
    [t].[matches_played] AS [matches_played],
    [t].[matches_won] AS [matches_won],
    [t].[matches_drawn] AS [matches_drawn],
    [t].[matches_lost] AS [matches_lost],
    [t].[goals_for] AS [goals_for],
    [t].[goals_against] AS [goals_against],
    [t].[goal_difference] AS [goal_difference],
    [t].[points] AS [points]
FROM (
    SELECT
        [t].[league_code] AS [league],
        [s].[season] AS [season],
        [t].[team] AS [team],
        SUM(
            CASE
                WHEN [t].[team] = [s].[home_team] THEN 1
                WHEN [t].[team] = [s].[away_team] THEN 1
                ELSE 0
            END
        ) AS [matches_played],
        SUM(
            CASE
                WHEN [t].[team] = [s].[home_team] AND [s].[home_score] > [s].[away_score] THEN 1
                WHEN [t].[team] = [s].[away_team] AND [s].[away_score] > [s].[home_score] THEN 1
                ELSE 0
            END
        ) AS [matches_won],
        SUM(
            CASE
                WHEN [t].[team] = [s].[home_team] AND [s].[home_score] = [s].[away_score] THEN 1
                WHEN [t].[team] = [s].[away_team] AND [s].[away_score] = [s].[home_score] THEN 1
                ELSE 0
            END
        ) AS [matches_drawn],
        SUM(
            CASE
                WHEN [t].[team] = [s].[home_team] AND [s].[home_score] < [s].[away_score] THEN 1
                WHEN [t].[team] = [s].[away_team] AND [s].[away_score] < [s].[home_score] THEN 1
                ELSE 0
            END
        ) AS [matches_lost],
        SUM(
            CASE
                WHEN [s].[status] <> 'FINISHED' THEN 0
                WHEN [t].[team] = [s].[home_team] THEN [s].[home_score]
                WHEN [t].[team] = [s].[away_team] THEN [s].[away_score]
                ELSE 0
            END
        ) AS [goals_for],
        SUM(
            CASE
                WHEN [s].[status] <> 'FINISHED' THEN 0
                WHEN [t].[team] = [s].[home_team] THEN [s].[away_score]
                WHEN [t].[team] = [s].[away_team] THEN [s].[home_score]
                ELSE 0
            END
        ) AS [goals_against],
        SUM(
            CASE
                WHEN [s].[status] <> 'FINISHED' THEN 0
                WHEN [t].[team] = [s].[home_team] THEN [s].[home_score] - [s].[away_score]
                ELSE [s].[away_score] - [s].[home_score]
            END
        ) AS [goal_difference],
        SUM(
            CASE
                WHEN [s].[status] <> 'FINISHED' THEN 0
                WHEN [t].[team] = [s].[home_team] AND [s].[home_score] > [s].[away_score] THEN 3
                WHEN [t].[team] = [s].[away_team] AND [s].[away_score] > [s].[home_score] THEN 3
                WHEN [t].[team] = [s].[home_team] AND [s].[home_score] < [s].[away_score] THEN 0
                WHEN [t].[team] = [s].[away_team] AND [s].[away_score] < [s].[home_score] THEN 0
                ELSE 1
            END
        ) AS [points]
    FROM (
        SELECT
            DISTINCT [m].[home_team] AS [team],
            [l].[code] AS [league_code]
        FROM [MATCHES] AS [m]
            INNER JOIN [LEAGUES] AS [l] ON [m].[league_id] = [l].[id]
    ) AS [t]
        INNER JOIN (
            SELECT
                [l].[code] AS [league_code],
                [m].[id] AS [id],
                [m].[status] AS [status],
                [m].[home_team] AS [home_team],
                [m].[away_team] AS [away_team],
                [m].[match_date] AS [match_date],
                [m].[home_score] AS [home_score],
                [m].[away_score] AS [away_score],
                CASE
                    WHEN CAST(strftime('%m', [m].[match_date]) AS INTEGER) < 8 THEN CAST((CAST(strftime('%Y', [m].[match_date]) AS INTEGER) - 1) AS TEXT)
                         || '/'
                         || SUBSTR(strftime('%Y', [m].[match_date]), 3, 2)
                    ELSE strftime('%Y', [m].[match_date])
                         || '/'
                         || SUBSTR(CAST((CAST(strftime('%Y', [m].[match_date]) AS INTEGER) + 1) AS TEXT), 3, 2)
                END AS [season]
            FROM MATCHES AS [m]
            INNER JOIN LEAGUES AS [l] ON [m].[league_id] = [l].[id]
        ) AS [s] ON ([t].[league_code] = [s].[league_code] AND ([s].[home_team] = [t].[team] OR [s].[away_team] = [t].[team]))
    GROUP BY [t].[league_code], [s].[season], [t].[team]
) AS [t]
ORDER BY [t].[league], [t].[season], t.[points] DESC, [t].[goal_difference] DESC, [t].[goals_for] DESC;


CREATE VIEW SCHEDULED_MATCHES AS
SELECT
    [l].[code] AS [league],
    [m].[matchday] AS [matchday],
    [m].[match_date] AS [match_date]
FROM [LEAGUES] AS [l]
INNER JOIN [MATCHES] AS [m] ON [m].[league_id] = [l].[id]
LEFT JOIN (
    SELECT
        [m].[match_date] AS [match_date]
    FROM [MATCHES] AS [m]
    INNER JOIN [ROUNDS] AS [r] ON [m].[match_date] >= [r].[start_date]
    WHERE [r].[end_date] IS NULL
    AND [m].[status] <> 'FINISHED'
    AND [m].[use_match] = 1
    ORDER BY [m].[match_date] DESC
    LIMIT 1
) as [ngw]
WHERE [m].[status] <> 'FINISHED'
AND [m].[use_match] = 1
AND [m].[match_date] <= [ngw].[match_date];


CREATE VIEW WORLDCUP_SCORES AS
SELECT
    [a_pl].[first_name] || ' ' || [a_pl].[last_name] AS [player],
    COALESCE([a].[score], 0) AS [score],
    COALESCE([a].[bonus], 0) AS [bonus],
    COALESCE([a].[total], 0) AS [total]
FROM WORLDCUP_PLAYERS AS [a_pl]
LEFT JOIN (
    SELECT
        [t].[player_id] AS [player_id],
        COALESCE(SUM([t].[score]), 0) AS [score],
        SUM([t].[bonus]) AS [bonus],
        SUM([t].[score]) + SUM([t].[bonus]) AS [total]
    FROM (
        SELECT
            [s].[player_id] AS [player_id],
            [s].[score] AS [score],
            CASE
                WHEN [s].[score] > 0 THEN [s].[bonus]
                ELSE 0
            END AS [bonus]
        FROM (
            SELECT
                [pl].[id] AS [player_id],
                [m].[home_team] AS [home_team],
                [m].[away_team] AS [away_team],
                [pr].[prediction] AS [prediction],
                CASE
                    WHEN [pr].[prediction] = 'home' AND [m].[home_score] > [m].[away_score] THEN 1
                    WHEN [pr].[prediction] = 'away' AND [m].[away_score] > [m].[home_score] THEN 1
                    WHEN [pr].[prediction] = 'draw' AND [m].[home_score] = [m].[away_score] THEN 1
                    ELSE 0
                END AS [score],
                CASE
                    WHEN [pr].[plus_ninety] = 1 AND [pr].[penalties] = 1 AND [m].[penalties] = 1 THEN 3
                    WHEN [pr].[plus_ninety] = 1 AND [pr].[extra_time] = 1 AND [m].[extra_time] = 1 THEN 2
                    WHEN [pr].[plus_ninety] = 0 AND [m].[extra_time] = 0 AND [m].[penalties] = 0 THEN 1
                    ELSE 0
                END AS [bonus]
            FROM WORLDCUP_PREDICTIONS AS [pr]
            JOIN WORLDCUP_MATCHES AS [m] ON [pr].[match_id] = [m].[id]
            JOIN WORLDCUP_PLAYERS [pl] ON [pr].[player_id] = [pl].[id]
            WHERE [m].[status] = 'FINISHED'
        ) AS [s]
    ) AS [t]
    GROUP BY [t].[player_id]
) AS [a] ON [a_pl].[id] = [a].[player_id]
ORDER BY COALESCE([a].[total], 0) DESC;
