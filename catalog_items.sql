-- Table definitions for the catalog project

DROP DATABASE if exists catalog;

CREATE DATABASE catalog;
\c catalog;

CREATE TABLE users
(
  id serial primary key,
  name text,
  email text
);

CREATE TABLE categories
(
  name text primary key
);

CREATE TABLE items
(
  name text primary key,
  description text,
  user_id int references users
);

CREATE TABLE category_items
(
  category text references categories on update cascade on delete cascade,
  item text references items on update cascade on delete cascade
);
