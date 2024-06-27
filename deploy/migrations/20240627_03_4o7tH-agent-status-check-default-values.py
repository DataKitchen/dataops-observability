"""
Agent status check default values
"""

from yoyo import step

__depends__ = {"20240627_02_ORQ6B-adding-agent-status-check-config-column"}

steps = [
    step("UPDATE `project` SET `agent_status_check_interval` = 300"),
    step("UPDATE `agent` SET `status` = 'ONLINE'"),
]
