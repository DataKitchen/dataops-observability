-- Initial Schema
-- depends:
-- transactional: false

DROP TABLE `user_role_through_table`;
DROP TABLE `test_outcome_integration`;
DROP TABLE `test_outcome`;
DROP TABLE `testgen_dataset_component`;
DROP TABLE `service_account_key`;
DROP TABLE `schedule`;
DROP TABLE `run_alerts`;
DROP TABLE `rule`;
DROP TABLE `rbac_role`;
DROP TABLE `journey_dag_edge`;
DROP TABLE `instances_instancesets`;
DROP TABLE `instances_rules`;
DROP TABLE `instance_alerts_components`;
DROP TABLE `instance_alerts`;
DROP TABLE `instance`;
DROP TABLE `journey`;
DROP TABLE `evententity`;
DROP TABLE `run_task`;
DROP TABLE `run`;
DROP TABLE `task`;
DROP TABLE `dataset_operation`;
DROP TABLE `instance_set`;
DROP TABLE `component`;
DROP TABLE `auth_provider`;
DROP TABLE `api_key`;
DROP TABLE `agent`;
DROP TABLE `project`;
DROP TABLE `organization`;
DROP TABLE `action`;
ALTER TABLE `company` DROP FOREIGN KEY `fk_company_created_by_id_refs_user`;
DROP TABLE `user`;
DROP TABLE `company`;
