from datetime import datetime, timezone, timedelta

from apscheduler.triggers.interval import IntervalTrigger
from peewee import Select

from common.agent import handle_agent_status_change
from common.entities import Project, Agent
from common.entities.agent import AgentStatus
from conf import settings
from scheduler.schedule_source import ScheduleSource


def _get_agent_status(check_interval_seconds: int, latest_heartbeat: datetime) -> AgentStatus:
    lateness = (datetime.now(tz=timezone.utc) - latest_heartbeat).total_seconds()
    if lateness > check_interval_seconds * settings.AGENT_STATUS_CHECK_OFFLINE_FACTOR:
        return AgentStatus.OFFLINE
    elif lateness > check_interval_seconds * settings.AGENT_STATUS_CHECK_UNHEALTHY_FACTOR:
        return AgentStatus.UNHEALTHY
    else:
        return AgentStatus.ONLINE


def _check_agents_are_online(project: Project) -> None:
    check_threshold = datetime.now(tz=timezone.utc) - timedelta(seconds=project.agent_status_check_interval)
    for agent in Agent.select().where(
        Agent.project == project.id,
        Agent.latest_heartbeat < check_threshold,
    ):
        new_status = _get_agent_status(project.agent_status_check_interval, agent.latest_heartbeat)
        if handle_agent_status_change(agent, new_status):
            agent.save()


class AgentStatusScheduleSource(ScheduleSource):
    source_name = "agent_status"

    def _get_schedules(self) -> Select:
        return Project.select().where(Project.agent_status_check_interval > 0)

    def _create_and_add_job(self, schedule: Project) -> None:
        self.add_job(
            _check_agents_are_online,
            str(schedule.id),
            IntervalTrigger(seconds=schedule.agent_status_check_interval),
            {"project": schedule},
        )
