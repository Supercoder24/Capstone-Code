-- Delete tables if exist
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS access;
DROP TABLE IF EXISTS rooms;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE access (
  user_id INTEGER NOT NULL,
  room_id INTEGER NOT NULL,
  admin BOOLEAN NOT NULL,
  last_accessed TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP -- TODO: Set timestamp to some other default value
);

CREATE TABLE rooms (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  roomname TEXT UNIQUE NOT NULL,
  ip TEXT NOT NULL,
  windows INTEGER NOT NULL,
  override BOOLEAN NOT NULL,
  main TEXT,
  variables TEXT
); -- TODO: Add last updated timestamp to rooms

CREATE TABLE schedule (
  room_id INTEGER NOT NULL,
  countdown TEXT NOT NULL,
  days TEXT NOT NULL,
  vars TEXT NOT NULL,
  tod TEXT NOT NULL,
  event_name TEXT NOT NULL
  );
