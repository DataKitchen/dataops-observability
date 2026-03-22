"""
Add component_include_patterns and component_exclude_patterns columns to journey table
"""

from yoyo import step

__depends__ = {"20240723_01_K3c3Q-renaming-the-agent-check-interval-column"}
__transactional__ = False

steps = [
    step(
        "ALTER TABLE `journey` ADD COLUMN `component_include_patterns` varchar(255) NULL",
        "ALTER TABLE `journey` DROP COLUMN `component_include_patterns`",
    ),
    step(
        "ALTER TABLE `journey` ADD COLUMN `component_exclude_patterns` varchar(255) NULL",
        "ALTER TABLE `journey` DROP COLUMN `component_exclude_patterns`",
    ),
]
