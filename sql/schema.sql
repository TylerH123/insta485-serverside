PRAGMA foreign_keys = ON;

CREATE TABLE users(
  username VARCHAR(20) NOT NULL,
  fullname VARCHAR(40) NOT NULL,
  email VARCHAR(40) NOT NULL,
  filename VARCHAR(64) NOT NULL, 
  password VARCHAR(256) NOT NULL,
  created DATETIME DEFAULT(getdate()), 
  PRIMARY KEY(username)
);

CREATE TABLE posts(
  postid INTEGER AUTO_INCREMENT,
  filename VARCHAR(64) NOT NULL,
  owner VARCHAR(20),
  created DATETIME DEFAULT(getdate()), 
  PRIMARY KEY(postid),
  FOREIGN KEY(owner) REFERENCES users
    ON DELETE CASCADE 
);

CREATE TABLE following(
  username1 VARCHAR(20),
  username2 VARCHAR(20),
  created DATETIME DEFAULT(getdate()), 
  PRIMARY KEY(username1, username2)
  FOREIGN KEY(username1) REFERENCES users
    ON DELETE CASCADE,
  FOREIGN KEY(username2) REFERENCES users
    ON DELETE CASCADE 
);

CREATE TABLE comments(
  commentid INTEGER AUTO_INCREMENT,
  owner VARCHAR(20), 
  postid INTEGER, 
  text VARCHAR(1024),
  created DATETIME DEFAULT(getdate()),
  PRIMARY KEY(commentid),
  FOREIGN KEY(owner) REFERENCES users
    ON DELETE CASCADE,
  FOREIGN KEY(postid) REFERENCES posts
    ON DELETE CASCADE
);

CREATE TABle likes(
  likeid INTEGER AUTO_INCREMENT,
  owner VARCHAR(20),
  postid INTEGER,
  created DATETIME DEFAULT(getdate()),
  FOREIGN KEY(owner) REFERENCES users
    ON DELETE CASCADE,
  FOREIGN KEY(postid) REFERENCES posts
    ON DELETE CASCADe
);