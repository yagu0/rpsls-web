-- A user may or may not play games
create table Users(
  id integer primary key,
  name varchar(32) unique not null
);

create table Games(
  id integer primary key,
  created date
);

-- A player (ref. uid) is involved into a game (ref. gid)
create table Players(
  uid integer,
  gid integer,
  points integer not null default 0,
  foreign key(uid) references Users(id),
  foreign key(gid) references Games(id)
);

create table Moves(
  uid integer,
  gid integer,
  choice character(1) not null, --'r', 'p', 's', 'l' or 'k'
  mnum integer not null,
  foreign key(uid) references Users(id),
  foreign key(gid) references Games(id)
);
