-- Table definitions for the catalog project

DROP DATABASE if exists catalog;

CREATE DATABASE catalog;
\c catalog;

CREATE TABLE categories
(
  name text primary key
);

CREATE TABLE items
(
  name text primary key,
  description text
);

CREATE TABLE category_items
(
  category text references categories not null,
  item text references items not null
);
