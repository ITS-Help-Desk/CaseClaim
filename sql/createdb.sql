CREATE TABLE `CheckedClaims`(
    `checker_message_id` BIGINT UNSIGNED NOT NULL,
    `case_num` VARCHAR(8) NOT NULL,
    `tech_id` BIGINT UNSIGNED NOT NULL,
    `lead_id` BIGINT UNSIGNED NOT NULL,
    `claim_time` TIMESTAMP NOT NULL,
    `complete_time` TIMESTAMP NOT NULL,
    `check_time` TIMESTAMP NOT NULL,
    `status` VARCHAR(255) NOT NULL,
    `ping_thread_id` BIGINT UNSIGNED NULL
);
ALTER TABLE
    `CheckedClaims` ADD PRIMARY KEY(`checker_message_id`);
CREATE TABLE `PendingPings`(
    `checker_message_id` BIGINT UNSIGNED NOT NULL,
    `severity` VARCHAR(255) NOT NULL,
    `description` MEDIUMTEXT NOT NULL
);
CREATE TABLE `Announcements`(
    `message_id` BIGINT UNSIGNED NOT NULL,
    `case_message_id` BIGINT UNSIGNED NOT NULL,
    `title` VARCHAR(255) NOT NULL,
    `description` MEDIUMTEXT NOT NULL,
    `user` BIGINT UNSIGNED NOT NULL,
    `end_time` DATETIME NOT NULL,
    `active` TINYINT(1) NOT NULL
);
ALTER TABLE
    `Announcements` ADD PRIMARY KEY(`message_id`);
ALTER TABLE
    `Announcements` ADD UNIQUE `announcements_case_message_id_unique`(`case_message_id`);
CREATE TABLE `Pings`(
    `thread_id` BIGINT UNSIGNED NOT NULL,
    `message_id` BIGINT UNSIGNED NOT NULL,
    `severity` VARCHAR(255) NOT NULL,
    `description` MEDIUMTEXT NOT NULL
);
ALTER TABLE
    `Pings` ADD PRIMARY KEY(`thread_id`);
ALTER TABLE
    `Pings` ADD UNIQUE `pings_message_id_unique`(`message_id`);
CREATE TABLE `Teams`(
    `role_id` BIGINT UNSIGNED NOT NULL,
    `color` VARCHAR(7) NOT NULL,
    `image_url` MEDIUMTEXT NOT NULL,
    `points` BIGINT NOT NULL
);
ALTER TABLE
    `Teams` ADD PRIMARY KEY(`role_id`);
CREATE TABLE `Outages`(
    `message_id` BIGINT UNSIGNED NOT NULL,
    `case_message_id` BIGINT NOT NULL,
    `service` VARCHAR(255) NOT NULL,
    `parent_case` VARCHAR(255) NULL,
    `description` MEDIUMTEXT NOT NULL,
    `troubleshooting_steps` MEDIUMTEXT NULL,
    `resolution_time` VARCHAR(255) NULL,
    `user` BIGINT UNSIGNED NOT NULL,
    `active` TINYINT(1) NOT NULL
);
ALTER TABLE
    `Outages` ADD PRIMARY KEY(`message_id`);
ALTER TABLE
    `Outages` ADD UNIQUE `outages_case_message_id_unique`(`case_message_id`);
CREATE TABLE `CompletedClaims`(
    `checker_message_id` BIGINT UNSIGNED NOT NULL,
    `case_num` VARCHAR(8) NOT NULL,
    `tech_id` BIGINT UNSIGNED NOT NULL,
    `claim_time` TIMESTAMP NOT NULL,
    `complete_time` TIMESTAMP NOT NULL
);
ALTER TABLE
    `CompletedClaims` ADD PRIMARY KEY(`checker_message_id`);
CREATE TABLE `Users`(
    `discord_id` BIGINT UNSIGNED NOT NULL,
    `first_name` VARCHAR(255) NOT NULL,
    `last_name` VARCHAR(255) NOT NULL,
    `team` BIGINT UNSIGNED NULL
);
ALTER TABLE
    `Users` ADD PRIMARY KEY(`discord_id`);
CREATE TABLE `ActiveClaims`(
    `claim_message_id` BIGINT UNSIGNED NOT NULL,
    `case_num` VARCHAR(8) NOT NULL,
    `tech_id` BIGINT UNSIGNED NOT NULL,
    `claim_time` TIMESTAMP NOT NULL
);
ALTER TABLE
    `ActiveClaims` ADD PRIMARY KEY(`claim_message_id`);
ALTER TABLE
    `ActiveClaims` ADD UNIQUE `activeclaims_case_num_unique`(`case_num`);
ALTER TABLE
    `PendingPings` ADD CONSTRAINT `pendingpings_checker_message_id_foreign` FOREIGN KEY(`checker_message_id`) REFERENCES `CheckedClaims`(`checker_message_id`);
ALTER TABLE
    `Users` ADD CONSTRAINT `users_team_foreign` FOREIGN KEY(`team`) REFERENCES `Teams`(`role_id`);
ALTER TABLE
    `CompletedClaims` ADD CONSTRAINT `completedclaims_tech_id_foreign` FOREIGN KEY(`tech_id`) REFERENCES `Users`(`discord_id`);
ALTER TABLE
    `CheckedClaims` ADD CONSTRAINT `checkedclaims_tech_id_foreign` FOREIGN KEY(`tech_id`) REFERENCES `Users`(`discord_id`);
ALTER TABLE
    `Outages` ADD CONSTRAINT `outages_user_foreign` FOREIGN KEY(`user`) REFERENCES `Users`(`discord_id`);
ALTER TABLE
    `CheckedClaims` ADD CONSTRAINT `checkedclaims_ping_thread_id_foreign` FOREIGN KEY(`ping_thread_id`) REFERENCES `Pings`(`thread_id`);
ALTER TABLE
    `CheckedClaims` ADD CONSTRAINT `checkedclaims_lead_id_foreign` FOREIGN KEY(`lead_id`) REFERENCES `Users`(`discord_id`);
ALTER TABLE
    `ActiveClaims` ADD CONSTRAINT `activeclaims_tech_id_foreign` FOREIGN KEY(`tech_id`) REFERENCES `Users`(`discord_id`);
ALTER TABLE
    `Announcements` ADD CONSTRAINT `announcements_user_foreign` FOREIGN KEY(`user`) REFERENCES `Users`(`discord_id`);