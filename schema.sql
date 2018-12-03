CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
-- DROP TABLE Pictures CASCADE;
-- DROP TABLE Users CASCADE;
-- DROP TABLE UserFriends CASCADE;
-- DROP TABLE Albums CASCADE;
-- DROP TABLE Tags CASCADE;
-- DROP TABLE Likes CASCADE;
-- DROP TABLE Comments CASCADE;
-- DROP TABLE PictureTag;
-- SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
-- SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=1;
SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;

CREATE TABLE IF NOT EXISTS Users
(
    user_id int4 AUTO_INCREMENT,
    firstname varchar(255),
    lastname varchar(255),
    email varchar(255) UNIQUE,
    password varchar(255),
    date_of_birth DATE NOT NULL,
    profilepic LONGBLOB,
    bio varchar(500),
    hometown varchar(255) NOT NULL,
    gender varchar(255) NOT NULL,
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS UserFriends
(
    user_id int4(11),
    f_email varchar(255),
    f_firstname varchar(255) NOT NULL,
    f_lastname varchar(255) NOT NULL,
 -- CONSTRAINT f_email_pk PRIMARY KEY (f_email),
  CONSTRAINT f_users_id_fk FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Albums
(
    album_id int4 AUTO_INCREMENT,
    user_id int4,
    name varchar(255),
    date_of_creation DATE,
  CONSTRAINT album_pk PRIMARY KEY (album_id),
  CONSTRAINT user_id_fk FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Pictures
(
    picture_id int4  AUTO_INCREMENT,
    user_id int4,
    imgdata longblob,
    caption varchar(255),
    album_id int4,
    INDEX upid_idx (user_id),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id),
  CONSTRAINT p_user_id FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  CONSTRAINT album_id_fk FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Tags
(
    description varchar(255) NOT NULL,
  CONSTRAINT description_pk PRIMARY KEY (description)
);

CREATE TABLE IF NOT EXISTS PictureTag
(
    picture_id int4,
    description varchar(255),
  CONSTRAINT t_picture_id_fk FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE,
  CONSTRAINT description_fk FOREIGN KEY (description) REFERENCES Tags(description) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Likes
(
    like_id int4 AUTO_INCREMENT,
    user_id int4(11),
    email varchar(255),
    picture_id int4,
  CONSTRAINT like_id_pk PRIMARY KEY (like_id),
  CONSTRAINT l_user_id_fk FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  CONSTRAINT l_email_fk FOREIGN KEY (email) REFERENCES Users(email) ON DELETE CASCADE,
  CONSTRAINT l_picture_id_fk FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Comments
(
    comment_id int4 AUTO_INCREMENT,
    text varchar(255),
    user_id int4,
    email varchar(255) UNIQUE,
    picture_id int4,
    date_comment_left DATE,
  CONSTRAINT comment_id_pk PRIMARY KEY (comment_id),
  CONSTRAINT c_email_fk FOREIGN KEY (email) REFERENCES Users(email) ON DELETE CASCADE,
  CONSTRAINT c_user_id_fk FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  CONSTRAINT c_picture_id_fk FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE
);


-- INSERT INTO Users (firstname, lastname, email, password, date_of_birth, bio, hometown, gender) VALUES ('firstf', 'firstl', 'first@email.com', 'first', '2018-01-01', 'Hi I love photos', 'Miami', 'femme');

-- INSERT INTO Users (firstname, lastname, email, password, date_of_birth, bio, hometown, gender) VALUES ('defaultf', 'defaultl', 'default@default.com', 'default', '2018-01-01', 'Default Loves Photos', 'Default', 'default');
