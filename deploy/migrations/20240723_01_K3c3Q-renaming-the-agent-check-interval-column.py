"""
Renaming the agent check interval column
"""

from yoyo import step

__depends__ = {"20240705_01_37l4A-set-project-alert-config-default"}

steps = [
    step(
        "ALTER TABLE `project` RENAME COLUMN `agent_status_check_interval` TO `agent_check_interval`",
        "ALTER TABLE `project` RENAME COLUMN `agent_check_interval` TO `agent_status_check_interval`",
    ),
]
