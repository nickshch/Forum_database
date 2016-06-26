DROP DATABASE IF EXISTS forum_database_last;
CREATE DATABASE forum_database_last;
USE forum_database_last;

DROP TABLE IF EXISTS `Forum`;

CREATE TABLE `Forum`(
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `name` VARCHAR (50) NOT NULL,
    `short_name` VARCHAR (35) NOT NULL,
    `user` VARCHAR (30) NOT NULL,

    PRIMARY KEY (`id`),
    UNIQUE KEY `name` (`name`),
    UNIQUE KEY `short_name` (`short_name`),
    KEY `user` (`user`)
) ENGINE = MYISAM;

DROP TABLE IF EXISTS `Post`;

CREATE TABLE `Post` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `forum` VARCHAR (50) NOT NULL,
    `thread` INT(11) NOT NULL,
    `user` VARCHAR (30) NOT NULL,
    `message` TEXT NOT NULL,
    `date` DATETIME NOT NULL,
    `likes` SMALLINT NOT NULL DEFAULT 0,
    `dislikes` SMALLINT NOT NULL DEFAULT 0,
    `points` SMALLINT NOT NULL DEFAULT 0,
    `parent` INT(11),
    `isHighlighted` BOOL NOT NULL DEFAULT False,
    `isApproved` BOOL NOT NULL DEFAULT False,
    `isEdited` BOOL NOT NULL DEFAULT False,
    `isSpam` BOOL NOT NULL DEFAULT False,
    `isDeleted` BOOL NOT NULL DEFAULT False,
    `path` VARCHAR(255) NOT NULL DEFAULT '',
    PRIMARY KEY (`id`),
    KEY `parent` (`parent`),
    KEY `thread` (`thread`),
    KEY `forum4` (`forum`, `thread`, `user`, `message`(10)),
    KEY `forum2` (`forum`, `date`),
    KEY `thread2` (`thread`, `date`),
    KEY `user2` (`user`, `date`)
) ENGINE = MYISAM;

DROP TABLE IF EXISTS `User`;

CREATE TABLE `User`(
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`username` VARCHAR (20) DEFAULT NULL,
  `email` VARCHAR (30) NOT NULL,
	`about` TEXT DEFAULT NULL,
	`name` VARCHAR (20) DEFAULT NULL,
	`isAnonymous` BOOL NOT NULL DEFAULT False,

	PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `name` (`name`)
) ENGINE = MYISAM;

DROP TABLE IF EXISTS `Thread`;

CREATE TABLE `Thread` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `forum` VARCHAR (50) NOT NULL,
    `user` VARCHAR (30) NOT NULL,
    `title` VARCHAR (50) NOT NULL,
    `date` DATETIME NOT NULL,
    `message` TEXT NOT NULL,
    `slug` VARCHAR (50) NOT NULL,
    `isDeleted` BOOL NOT NULL DEFAULT False,
    `isClosed` BOOL NOT NULL DEFAULT False,
    `likes` SMALLINT NOT NULL DEFAULT 0,
    `dislikes` SMALLINT NOT NULL DEFAULT 0,
    `points` SMALLINT NOT NULL DEFAULT 0,
    `posts` SMALLINT NOT NULL DEFAULT 0,

    PRIMARY KEY (`id`),
    KEY `forum4` (`forum`, `title`, `user`, `slug`),
    KEY `forum2` (`forum`, `date`),
    KEY `user2` (`user`, `date`)
) ENGINE = MYISAM;

DROP TABLE IF EXISTS `Follow`;

CREATE TABLE `Follow` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `follower` VARCHAR (30) NOT NULL,
    `followee` VARCHAR (30) NOT NULL,

    PRIMARY KEY (`id`),
    UNIQUE KEY `both` (`follower`,`followee`),
    KEY `follower` (`follower`),
    KEY `followee` (`followee`)
) ENGINE = MYISAM;

DROP TABLE IF EXISTS `Subscribe`;

CREATE TABLE `Subscribe` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `user` VARCHAR (30) NOT NULL,
    `thread` INT(11) NOT NULL,

    PRIMARY KEY (`id`),
    UNIQUE KEY `both` (`user`,`thread`),
    KEY (`user`),
    KEY (`thread`)
) ENGINE = MYISAM;
