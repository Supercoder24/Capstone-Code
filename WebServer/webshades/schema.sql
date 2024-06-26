-- Delete tables if exist
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS access;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS schedule;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  admin BOOLEAN NOT NULL,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE access (
  user_id INTEGER NOT NULL,
  room_id INTEGER NOT NULL,
  last_accessed TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP -- TODO: Set timestamp to some other default value
);

CREATE TABLE rooms (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  roomname TEXT UNIQUE NOT NULL,
  ip TEXT NOT NULL,
  windows INTEGER NOT NULL,
  override BOOLEAN NOT NULL,
  main TEXT,
  variables TEXT,
  last_schedule TEXT NOT NULL
); -- TODO: Add last updated timestamp to rooms

CREATE TABLE schedule (
  room_id INTEGER NOT NULL,
  countdown TEXT NOT NULL,
  day_string TEXT NOT NULL,
  vars TEXT NOT NULL,
  tod TEXT NOT NULL,
  event_name TEXT NOT NULL,
  id INTEGER PRIMARY KEY AUTOINCREMENT
  );

INSERT INTO users (username, password, admin) VALUES ('admin', 
'scrypt:32768:8:1$5wSzu8WLn0AFmsS6$fdda1b7dde224e08481e02a8217ef6f220eff26a53e51b948b2873ef925b9da6f33dc8ea13b49839dd115115f9cd7d5e68264dd26186a6781777eff72edf19c8',
True);

-- Test room:
-- INSERT INTO rooms (roomname, ip, windows, override, main, variables) VALUES ('I have no clue', '172.28.0.11', 1, false, 'a50', 'm85')
-- INSERT INTO access (user_id, room_id, last_accessed) VALUES (1, 1, '2024-03-22 14:40:19')
