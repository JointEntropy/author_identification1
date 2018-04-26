-- TABLE
CREATE TABLE author (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	bio TEXT NOT NULL, 
	img_url VARCHAR(1000) NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE composition (
	id INTEGER NOT NULL, 
	title VARCHAR(80) NOT NULL, 
	text TEXT NOT NULL, 
	features BLOB, 
	author_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(author_id) REFERENCES author (id)
);
CREATE TABLE user (
	id INTEGER NOT NULL, 
	username VARCHAR(80) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (username), 
	UNIQUE (email)
);
 
-- INDEX
 
-- TRIGGER
 
-- VIEW
 
