CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
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
  picos INTEGER NOT NULL,
  windows INTEGER NOT NULL,
  variables TEXT
); -- TODO: Add last updated timestamp to rooms

INSERT INTO users (username, password) VALUES ("felix", "password");
INSERT INTO rooms (roomname, ip, picos, windows) VALUES ("a210", "192.168.29.21", 2, 2);
INSERT INTO rooms (roomname, ip, picos, windows) VALUES ("a220", "192.168.29.22", 4, 8);
INSERT INTO rooms (roomname, ip, picos, windows) VALUES ("a230", "192.168.29.23", 4, 8);

INSERT INTO access (user_id, room_id) VALUES (1, 2);
INSERT INTO access (user_id, room_id) VALUES (1, 1);
INSERT INTO access (user_id, room_id) VALUES (1, 3);

SELECT room_id, roomname, ip, picos, windows FROM access
INNER JOIN rooms ON rooms.id=access.room_id
WHERE user_id = 1 order by last_accessed DESC;

/*
  Start by selecting a question by pressing 'Start' or 'View All Questions'.
  Use the resources and information about the database from the left panel to help.
  Press the run button to execute the query.
  Question is automatically validated every time you execute the query.
  Make your output match the expected output.
 
 
  Keybinds:
    [ctrl + enter]: Execute the SQL
    [ctrl + q]: Auto-format the SQL
*/