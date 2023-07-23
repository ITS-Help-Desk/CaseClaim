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
    `active` TINYINT(1) NOT NULL
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
    `CompletedClaims` ADD CONSTRAINT `completedclaims_tech_id_foreign` FOREIGN KEY(`tech_id`) REFERENCES `Users`(`discord_id`);
ALTER TABLE
    `CheckedClaims` ADD CONSTRAINT `checkedclaims_tech_id_foreign` FOREIGN KEY(`tech_id`) REFERENCES `Users`(`discord_id`);
ALTER TABLE
    `CheckedClaims` ADD CONSTRAINT `checkedclaims_ping_thread_id_foreign` FOREIGN KEY(`ping_thread_id`) REFERENCES `Pings`(`thread_id`);
ALTER TABLE
    `CheckedClaims` ADD CONSTRAINT `checkedclaims_lead_id_foreign` FOREIGN KEY(`lead_id`) REFERENCES `Users`(`discord_id`);
ALTER TABLE
    `ActiveClaims` ADD CONSTRAINT `activeclaims_tech_id_foreign` FOREIGN KEY(`tech_id`) REFERENCES `Users`(`discord_id`);