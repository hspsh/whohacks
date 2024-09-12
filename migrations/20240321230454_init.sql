-- Create "device" table
CREATE TABLE `device` (
 `mac_address` char NOT NULL,
 `hostname` varchar NULL,
 `last_seen` datetime NOT NULL,
 `user_id` integer NULL,
 `flags` integer NULL,
 PRIMARY KEY (`mac_address`),
 CONSTRAINT `0` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON UPDATE NO ACTION ON DELETE NO ACTION
);
-- Create "user" table
CREATE TABLE `user` (
 `id` integer NOT NULL,
 `username` varchar NOT NULL,
 `password` varchar NOT NULL,
 `display_name` varchar NOT NULL,
 `flags` integer NULL,
 PRIMARY KEY (`id`)
);
