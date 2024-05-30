CREATE DATABASE bobby_product_tracker;

\c bobby_product_tracker;

CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    user_id varchar(255) unique NOT NULL,
    user_name varchar(255) unique NOT NULL
);

CREATE TABLE products(
    id SERIAL PRIMARY KEY,
    fk_user_id int NOT NULL references users (id),
    category varchar NOT NULL,
    name varchar unique NOT NULL,
    start_price float NOT NULL,
    cur_price float NOT NULL,
    lowest_price float NOT NULL,
    lowest_price_date timestamp without time zone NOT NULL,
    tracked_since_date timestamp without time zone NOT NULL,
    url text NOT NULL,
    sale_bool boolean NOT NULL
);
