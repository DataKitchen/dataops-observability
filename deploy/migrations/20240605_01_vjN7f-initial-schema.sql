-- Initial Schema
-- depends:
-- transactional: false

CREATE TABLE `company` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `created_on` BIGINT NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `created_by_id` VARCHAR(40)
);

CREATE UNIQUE INDEX `company_name` ON `company` (`name`);

CREATE INDEX `company_created_by_id` ON `company` (`created_by_id`);

CREATE TABLE `action` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `name` VARCHAR(255) NOT NULL,
  `company_id` VARCHAR(40) NOT NULL,
  `action_impl` VARCHAR(255) NOT NULL,
  `action_args` JSON NOT NULL,
  FOREIGN KEY (`company_id`) REFERENCES `company` (`id`) ON DELETE CASCADE
);

CREATE INDEX `action_company_id` ON `action` (`company_id`);

CREATE UNIQUE INDEX `action_name_company_id` ON `action` (`name`, `company_id`);

CREATE TABLE `organization` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `created_on` BIGINT NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `description` VARCHAR(255),
  `company_id` VARCHAR(40) NOT NULL,
  `created_by_id` VARCHAR(40),
  FOREIGN KEY (`company_id`) REFERENCES `company` (`id`) ON DELETE CASCADE
);

CREATE INDEX `organization_company_id` ON `organization` (`company_id`);

CREATE INDEX `organization_created_by_id` ON `organization` (`created_by_id`);

CREATE UNIQUE INDEX `organization_company_id_name` ON `organization` (`company_id`, `name`);

CREATE TABLE `project` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `created_on` BIGINT NOT NULL,
  `active` BOOL NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `description` VARCHAR(255),
  `organization_id` VARCHAR(40) NOT NULL,
  `created_by_id` VARCHAR(40),
  FOREIGN KEY (`organization_id`) REFERENCES `organization` (`id`) ON DELETE CASCADE
);

CREATE INDEX `project_organization_id` ON `project` (`organization_id`);

CREATE INDEX `project_created_by_id` ON `project` (`created_by_id`);

CREATE UNIQUE INDEX `project_organization_id_name` ON `project` (`organization_id`, `name`);

CREATE TABLE `agent` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `key` VARCHAR(255) NOT NULL,
  `tool` VARCHAR(255) NOT NULL,
  `version` VARCHAR(255) NOT NULL,
  `project_id` VARCHAR(40) NOT NULL,
  `latest_heartbeat` BIGINT,
  `latest_event_timestamp` BIGINT,
  FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE
);

CREATE INDEX `agent_project_id` ON `agent` (`project_id`);

CREATE UNIQUE INDEX `agent_key_tool_project_id` ON `agent` (`key`, `tool`, `project_id`);

CREATE TABLE `user` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `created_on` BIGINT NOT NULL,
  `active` BOOL NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `foreign_user_id` VARCHAR(255),
  `primary_company_id` VARCHAR(40) NOT NULL,
  `username` VARCHAR(255),
  `password` VARCHAR(255),
  `salt` VARCHAR(255),
  `created_by_id` VARCHAR(40),
  FOREIGN KEY (`primary_company_id`) REFERENCES `company` (`id`) ON DELETE CASCADE,
  CONSTRAINT `username_special_character` CHECK ((not (username like '%%:%%')))
);

CREATE INDEX `user_email` ON `user` (`email`);

CREATE INDEX `user_foreign_user_id` ON `user` (`foreign_user_id`);

CREATE INDEX `user_primary_company_id` ON `user` (`primary_company_id`);

CREATE INDEX `user_created_by_id` ON `user` (`created_by_id`);

CREATE UNIQUE INDEX `user_primary_company_id_foreign_user_id` ON `user` (`primary_company_id`, `foreign_user_id`);

CREATE UNIQUE INDEX `user_primary_company_id_email` ON `user` (`primary_company_id`, `email`);

CREATE UNIQUE INDEX `user_username` ON `user` (`username`);

CREATE TABLE `api_key` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `digest` BLOB NOT NULL,
  `expiry` BIGINT NOT NULL,
  `user_id` VARCHAR(40) NOT NULL,
  FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
);

CREATE INDEX `apikey_user_id` ON `api_key` (`user_id`);

CREATE TABLE `auth_provider` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `client_id` VARCHAR(255) NOT NULL,
  `client_secret` VARCHAR(255) NOT NULL,
  `company_id` VARCHAR(40) NOT NULL,
  `discovery_doc_url` VARCHAR(255) NOT NULL,
  `domain` VARCHAR(255) NOT NULL,
  FOREIGN KEY (`company_id`) REFERENCES `company` (`id`)
);

CREATE INDEX `authprovider_company_id` ON `auth_provider` (`company_id`);

CREATE UNIQUE INDEX `authprovider_domain` ON `auth_provider` (`domain`);

CREATE TABLE `component` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `created_on` BIGINT NOT NULL,
  `updated_on` BIGINT NOT NULL,
  `key` VARCHAR(255) NOT NULL,
  `name` VARCHAR(255),
  `description` VARCHAR(255),
  `labels` JSON,
  `project_id` VARCHAR(40) NOT NULL,
  `type` VARCHAR(40) NOT NULL,
  `tool` VARCHAR(255),
  `created_by_id` VARCHAR(40),
  FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE
);

CREATE INDEX `component_project_id` ON `component` (`project_id`);

CREATE INDEX `component_created_by_id` ON `component` (`created_by_id`);

CREATE UNIQUE INDEX `component_project_id_key_type` ON `component` (`project_id`, `key`, `type`);

CREATE INDEX `component_project_id_key` ON `component` (`project_id`, `key`);

CREATE TABLE `instance_set` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `updated_on` BIGINT NOT NULL
);

CREATE TABLE `dataset_operation` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `dataset_id` VARCHAR(40) NOT NULL,
  `instance_set_id` VARCHAR(40),
  `operation_time` BIGINT NOT NULL,
  `operation` VARCHAR(10) NOT NULL,
  `path` VARCHAR(4096),
  FOREIGN KEY (`dataset_id`) REFERENCES `component` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`instance_set_id`) REFERENCES `instance_set` (`id`) ON DELETE SET NULL
);

CREATE INDEX `datasetoperation_dataset_id` ON `dataset_operation` (`dataset_id`);

CREATE INDEX `datasetoperation_instance_set_id` ON `dataset_operation` (`instance_set_id`);

CREATE INDEX `datasetoperation_operation_time` ON `dataset_operation` (`operation_time`);

CREATE TABLE `task` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `key` VARCHAR(255) NOT NULL,
  `name` VARCHAR(255),
  `description` TEXT NOT NULL,
  `required` BOOL NOT NULL,
  `pipeline_id` VARCHAR(40) NOT NULL,
  FOREIGN KEY (`pipeline_id`) REFERENCES `component` (`id`) ON DELETE CASCADE
);

CREATE INDEX `task_pipeline_id` ON `task` (`pipeline_id`);

CREATE UNIQUE INDEX `task_key_pipeline_id` ON `task` (`key`, `pipeline_id`);

CREATE TABLE `run` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `updated_on` BIGINT NOT NULL,
  `key` VARCHAR(255),
  `name` VARCHAR(1024),
  `start_time` BIGINT,
  `end_time` BIGINT,
  `expected_start_time` BIGINT,
  `expected_end_time` BIGINT,
  `pipeline_id` VARCHAR(40) NOT NULL,
  `instance_set_id` VARCHAR(40),
  `status` VARCHAR(255) NOT NULL,
  FOREIGN KEY (`pipeline_id`) REFERENCES `component` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`instance_set_id`) REFERENCES `instance_set` (`id`) ON DELETE SET NULL,
  CONSTRAINT `run_start_time_set` CHECK ((`start_time` IS NULL AND `status` IN ('PENDING',
  'MISSING')) OR (`start_time` IS NOT NULL AND `status` NOT IN ('PENDING',
  'MISSING'))),
  CONSTRAINT `run_key_set` CHECK ((`key` IS NULL AND `status` IN ('PENDING',
  'MISSING')) OR (`key` IS NOT NULL AND `status` NOT IN ('PENDING',
  'MISSING')))
);

CREATE INDEX `run_key` ON `run` (`key`);

CREATE INDEX `run_start_time` ON `run` (`start_time`);

CREATE INDEX `run_end_time` ON `run` (`end_time`);

CREATE INDEX `run_pipeline_id` ON `run` (`pipeline_id`);

CREATE INDEX `run_instance_set_id` ON `run` (`instance_set_id`);

CREATE INDEX `run_status` ON `run` (`status`);

CREATE UNIQUE INDEX `run_pipeline_id_key` ON `run` (`pipeline_id`, `key`);

CREATE TABLE `run_task` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `required` BOOL NOT NULL,
  `status` VARCHAR(255) NOT NULL,
  `start_time` BIGINT,
  `end_time` BIGINT,
  `run_id` VARCHAR(40) NOT NULL,
  `task_id` VARCHAR(40) NOT NULL,
  FOREIGN KEY (`run_id`) REFERENCES `run` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`task_id`) REFERENCES `task` (`id`) ON DELETE CASCADE
);

CREATE INDEX `runtask_run_id` ON `run_task` (`run_id`);

CREATE INDEX `runtask_task_id` ON `run_task` (`task_id`);

CREATE UNIQUE INDEX `runtask_run_id_task_id` ON `run_task` (`run_id`, `task_id`);

CREATE TABLE `evententity` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `version` INTEGER NOT NULL,
  `type` VARCHAR(40) NOT NULL,
  `created_timestamp` BIGINT NOT NULL,
  `timestamp` BIGINT,
  `project_id` VARCHAR(40) NOT NULL,
  `component_id` VARCHAR(40),
  `task_id` VARCHAR(40),
  `run_id` VARCHAR(40),
  `run_task_id` VARCHAR(40),
  `instance_set_id` VARCHAR(40),
  `v2_payload` JSON NOT NULL,
  FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`component_id`) REFERENCES `component` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`task_id`) REFERENCES `task` (`id`) ON DELETE SET NULL,
  FOREIGN KEY (`run_id`) REFERENCES `run` (`id`) ON DELETE SET NULL,
  FOREIGN KEY (`run_task_id`) REFERENCES `run_task` (`id`) ON DELETE SET NULL,
  FOREIGN KEY (`instance_set_id`) REFERENCES `instance_set` (`id`) ON DELETE SET NULL
);

CREATE INDEX `evententity_created_timestamp` ON `evententity` (`created_timestamp`);

CREATE INDEX `evententity_timestamp` ON `evententity` (`timestamp`);

CREATE INDEX `evententity_project_id` ON `evententity` (`project_id`);

CREATE INDEX `evententity_component_id` ON `evententity` (`component_id`);

CREATE INDEX `evententity_task_id` ON `evententity` (`task_id`);

CREATE INDEX `evententity_run_id` ON `evententity` (`run_id`);

CREATE INDEX `evententity_run_task_id` ON `evententity` (`run_task_id`);

CREATE INDEX `evententity_instance_set_id` ON `evententity` (`instance_set_id`);

CREATE TABLE `journey` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `created_on` BIGINT NOT NULL,
  `updated_on` BIGINT NOT NULL,
  `name` VARCHAR(255),
  `description` VARCHAR(255),
  `project_id` VARCHAR(40) NOT NULL,
  `created_by_id` VARCHAR(40),
  FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE
);

CREATE INDEX `journey_project_id` ON `journey` (`project_id`);

CREATE INDEX `journey_created_by_id` ON `journey` (`created_by_id`);

CREATE UNIQUE INDEX `journey_name_project_id` ON `journey` (`name`, `project_id`);

CREATE TABLE `instance` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `updated_on` BIGINT NOT NULL,
  `journey_id` VARCHAR(40) NOT NULL,
  `start_time` BIGINT NOT NULL,
  `end_time` BIGINT,
  `has_errors` BOOL NOT NULL,
  `has_warnings` BOOL NOT NULL,
  `payload_key` VARCHAR(255),
  `start_type` VARCHAR(50) NOT NULL,
  FOREIGN KEY (`journey_id`) REFERENCES `journey` (`id`) ON DELETE CASCADE
);

CREATE INDEX `instance_journey_id` ON `instance` (`journey_id`);

CREATE INDEX `instance_end_time` ON `instance` (`end_time`);

CREATE TABLE `instance_alerts` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `updated_on` BIGINT NOT NULL,
  `created_on` BIGINT NOT NULL,
  `name` VARCHAR(255),
  `details` JSON NOT NULL,
  `description` VARCHAR(255) NOT NULL,
  `level` VARCHAR(50) NOT NULL,
  `type` VARCHAR(100) NOT NULL,
  `instance_id` VARCHAR(40) NOT NULL,
  FOREIGN KEY (`instance_id`) REFERENCES `instance` (`id`) ON DELETE CASCADE
);

CREATE INDEX `instancealert_instance_id` ON `instance_alerts` (`instance_id`);

CREATE TABLE `instance_alerts_components` (
  `instance_alert_id` VARCHAR(40) NOT NULL,
  `component_id` VARCHAR(40) NOT NULL,
  PRIMARY KEY (`instance_alert_id`,
  `component_id`),
  FOREIGN KEY (`instance_alert_id`) REFERENCES `instance_alerts` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`component_id`) REFERENCES `component` (`id`) ON DELETE CASCADE
);

CREATE INDEX `instancealertscomponents_instance_alert_id` ON `instance_alerts_components` (`instance_alert_id`);

CREATE INDEX `instancealertscomponents_component_id` ON `instance_alerts_components` (`component_id`);

CREATE TABLE `instances_rules` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `updated_on` BIGINT NOT NULL,
  `journey_id` VARCHAR(40) NOT NULL,
  `action` VARCHAR(255) NOT NULL,
  `batch_pipeline_id` VARCHAR(40),
  `expression` VARCHAR(100),
  `timezone` VARCHAR(50),
  FOREIGN KEY (`journey_id`) REFERENCES `journey` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`batch_pipeline_id`) REFERENCES `component` (`id`) ON DELETE CASCADE,
  CONSTRAINT `component_xor_schedule` CHECK ((`batch_pipeline_id` IS NOT NULL AND `expression` IS NULL) OR (`batch_pipeline_id` IS NULL AND `expression` IS NOT NULL))
);

CREATE INDEX `instancerule_journey_id` ON `instances_rules` (`journey_id`);

CREATE INDEX `instancerule_batch_pipeline_id` ON `instances_rules` (`batch_pipeline_id`);

CREATE TABLE `instances_instancesets` (
  `updated_on` BIGINT NOT NULL,
  `instance_id` VARCHAR(40) NOT NULL,
  `instance_set_id` VARCHAR(40) NOT NULL,
  PRIMARY KEY (`instance_id`,
  `instance_set_id`),
  FOREIGN KEY (`instance_id`) REFERENCES `instance` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`instance_set_id`) REFERENCES `instance_set` (`id`) ON DELETE CASCADE
);

CREATE INDEX `instancesinstancesets_instance_id` ON `instances_instancesets` (`instance_id`);

CREATE INDEX `instancesinstancesets_instance_set_id` ON `instances_instancesets` (`instance_set_id`);

CREATE TABLE `journey_dag_edge` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `updated_on` BIGINT NOT NULL,
  `journey_id` VARCHAR(40) NOT NULL,
  `left_id` VARCHAR(40),
  `right_id` VARCHAR(40) NOT NULL,
  FOREIGN KEY (`journey_id`) REFERENCES `journey` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`left_id`) REFERENCES `component` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`right_id`) REFERENCES `component` (`id`) ON DELETE CASCADE
);

CREATE INDEX `journeydagedge_journey_id` ON `journey_dag_edge` (`journey_id`);

CREATE INDEX `journeydagedge_left_id` ON `journey_dag_edge` (`left_id`);

CREATE INDEX `journeydagedge_right_id` ON `journey_dag_edge` (`right_id`);

CREATE UNIQUE INDEX `journeydagedge_journey_id_left_id_right_id` ON `journey_dag_edge` (`journey_id`, `left_id`, `right_id`);

CREATE TABLE `rbac_role` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `name` VARCHAR(255) NOT NULL,
  `description` VARCHAR(255)
);

CREATE UNIQUE INDEX `role_name` ON `rbac_role` (`name`);

CREATE TABLE `rule` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `updated_on` BIGINT NOT NULL,
  `created_on` BIGINT NOT NULL,
  `component_id` VARCHAR(40),
  `journey_id` VARCHAR(40) NOT NULL,
  `rule_schema` VARCHAR(255) NOT NULL,
  `rule_data` JSON NOT NULL,
  `action` VARCHAR(50) NOT NULL,
  `action_args` JSON NOT NULL,
  FOREIGN KEY (`component_id`) REFERENCES `component` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`journey_id`) REFERENCES `journey` (`id`) ON DELETE CASCADE
);

CREATE INDEX `rule_component_id` ON `rule` (`component_id`);

CREATE INDEX `rule_journey_id` ON `rule` (`journey_id`);

CREATE TABLE `run_alerts` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `updated_on` BIGINT NOT NULL,
  `created_on` BIGINT NOT NULL,
  `name` VARCHAR(255),
  `details` JSON NOT NULL,
  `description` VARCHAR(255) NOT NULL,
  `level` VARCHAR(50) NOT NULL,
  `type` VARCHAR(100) NOT NULL,
  `run_id` VARCHAR(40) NOT NULL,
  FOREIGN KEY (`run_id`) REFERENCES `run` (`id`) ON DELETE CASCADE
);

CREATE INDEX `runalert_run_id` ON `run_alerts` (`run_id`);

CREATE TABLE `schedule` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `created_on` BIGINT NOT NULL,
  `updated_on` BIGINT NOT NULL,
  `created_by_id` VARCHAR(40),
  `component_id` VARCHAR(40) NOT NULL,
  `description` VARCHAR(300),
  `schedule` VARCHAR(100) NOT NULL,
  `timezone` VARCHAR(50) NOT NULL,
  `expectation` VARCHAR(50) NOT NULL,
  `margin` INTEGER,
  FOREIGN KEY (`component_id`) REFERENCES `component` (`id`) ON DELETE CASCADE
);

CREATE INDEX `schedule_created_by_id` ON `schedule` (`created_by_id`);

CREATE INDEX `schedule_component_id` ON `schedule` (`component_id`);

CREATE UNIQUE INDEX `schedule_component_id_expectation` ON `schedule` (`component_id`, `expectation`);

CREATE TABLE `service_account_key` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `description` VARCHAR(255),
  `digest` BLOB NOT NULL,
  `expiry` BIGINT NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `project_id` VARCHAR(40) NOT NULL,
  `allowed_services` JSON NOT NULL,
  FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE
);

CREATE INDEX `serviceaccountkey_project_id` ON `service_account_key` (`project_id`);

CREATE UNIQUE INDEX `serviceaccountkey_name_project_id` ON `service_account_key` (`name`, `project_id`);

CREATE TABLE `testgen_dataset_component` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `database_name` VARCHAR(255) NOT NULL,
  `connection_name` VARCHAR(255) NOT NULL,
  `schema` VARCHAR(255),
  `table_list` JSON NOT NULL,
  `table_include_pattern` VARCHAR(255),
  `table_exclude_pattern` VARCHAR(255),
  `table_group_id` VARCHAR(40),
  `project_code` VARCHAR(255),
  `uses_sampling` BOOL,
  `sample_percentage` VARCHAR(255),
  `sample_minimum_count` INTEGER,
  `component_id` VARCHAR(40) NOT NULL,
  FOREIGN KEY (`component_id`) REFERENCES `component` (`id`) ON DELETE CASCADE
);

CREATE UNIQUE INDEX `testgendatasetcomponent_component_id` ON `testgen_dataset_component` (`component_id`);

CREATE TABLE `test_outcome` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `updated_on` BIGINT NOT NULL,
  `component_id` VARCHAR(40) NOT NULL,
  `description` VARCHAR(255),
  `dimension` JSON NOT NULL,
  `end_time` BIGINT,
  `external_url` TEXT,
  `instance_set_id` VARCHAR(40),
  `key` VARCHAR(255),
  `metric_name` VARCHAR(40),
  `metric_description` VARCHAR(255),
  `max_threshold` NUMERIC(20,
  5),
  `metric_value` NUMERIC(20,
  5),
  `min_threshold` NUMERIC(20,
  5),
  `name` VARCHAR(255) NOT NULL,
  `result` TEXT,
  `run_id` VARCHAR(40),
  `start_time` BIGINT,
  `status` VARCHAR(255) NOT NULL,
  `task_id` VARCHAR(40),
  `type` VARCHAR(40),
  FOREIGN KEY (`component_id`) REFERENCES `component` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`instance_set_id`) REFERENCES `instance_set` (`id`) ON DELETE SET NULL,
  FOREIGN KEY (`run_id`) REFERENCES `run` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`task_id`) REFERENCES `task` (`id`) ON DELETE CASCADE
);

CREATE INDEX `testoutcome_component_id` ON `test_outcome` (`component_id`);

CREATE INDEX `testoutcome_end_time` ON `test_outcome` (`end_time`);

CREATE INDEX `testoutcome_instance_set_id` ON `test_outcome` (`instance_set_id`);

CREATE INDEX `testoutcome_key` ON `test_outcome` (`key`);

CREATE INDEX `testoutcome_run_id` ON `test_outcome` (`run_id`);

CREATE INDEX `testoutcome_status` ON `test_outcome` (`status`);

CREATE INDEX `testoutcome_task_id` ON `test_outcome` (`task_id`);

CREATE TABLE `test_outcome_integration` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `table` VARCHAR(255) NOT NULL,
  `columns` JSON,
  `test_suite` VARCHAR(255) NOT NULL,
  `version` INTEGER NOT NULL,
  `test_outcome_id` VARCHAR(40) NOT NULL,
  `test_parameters` JSON NOT NULL,
  FOREIGN KEY (`test_outcome_id`) REFERENCES `test_outcome` (`id`) ON DELETE CASCADE
);

CREATE INDEX `testgentestoutcomeintegration_test_outcome_id` ON `test_outcome_integration` (`test_outcome_id`);

CREATE TABLE `user_role_through_table` (
  `id` VARCHAR(40) NOT NULL PRIMARY KEY,
  `user_id` VARCHAR(40) NOT NULL,
  `role_id` VARCHAR(40) NOT NULL,
  FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`role_id`) REFERENCES `rbac_role` (`id`) ON DELETE CASCADE
);

CREATE INDEX `userrole_user_id` ON `user_role_through_table` (`user_id`);

CREATE INDEX `userrole_role_id` ON `user_role_through_table` (`role_id`);

ALTER TABLE `component` ADD CONSTRAINT `fk_component_created_by_id_refs_user` FOREIGN KEY (`created_by_id`) REFERENCES `user` (`id`) ON DELETE SET NULL;

ALTER TABLE `company` ADD CONSTRAINT `fk_company_created_by_id_refs_user` FOREIGN KEY (`created_by_id`) REFERENCES `user` (`id`) ON DELETE SET NULL;

ALTER TABLE `organization` ADD CONSTRAINT `fk_organization_created_by_id_refs_user` FOREIGN KEY (`created_by_id`) REFERENCES `user` (`id`) ON DELETE SET NULL;

ALTER TABLE `project` ADD CONSTRAINT `fk_project_created_by_id_refs_user` FOREIGN KEY (`created_by_id`) REFERENCES `user` (`id`) ON DELETE SET NULL;

ALTER TABLE `user` ADD CONSTRAINT `fk_user_created_by_id_refs_user` FOREIGN KEY (`created_by_id`) REFERENCES `user` (`id`) ON DELETE SET NULL;

ALTER TABLE `journey` ADD CONSTRAINT `fk_journey_created_by_id_refs_user` FOREIGN KEY (`created_by_id`) REFERENCES `user` (`id`) ON DELETE SET NULL;

ALTER TABLE `schedule` ADD CONSTRAINT `fk_schedule_created_by_id_refs_user` FOREIGN KEY (`created_by_id`) REFERENCES `user` (`id`) ON DELETE SET NULL;
