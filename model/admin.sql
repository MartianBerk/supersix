/*
 * SQLite Tables for Admin DB.
 */

CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    account_id TEXT NOT NULL
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    account TEXT NOT NULL,
    email TEXT NULL,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL
);
