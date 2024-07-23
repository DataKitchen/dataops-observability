import logging
from datetime import datetime, timezone, timedelta

from apscheduler.triggers.interval import IntervalTrigger
from peewee import Select

from common.entities import Project, Agent
from common.entities.agent import AgentStatus
from common.events.internal.system import AgentStatusChangeEvent
from common.kafka import TOPIC_IDENTIFIED_EVENTS
from conf import settings
from scheduler.schedule_source import ScheduleSource


LOG = logging.getLogger(__name__)


def _get_agent_status(check_interval_seconds: int, latest_heartbeat: datetime) -> AgentStatus:
    lateness = (datetime.now(tz=timezone.utc) - latest_heartbeat).total_seconds()
    if lateness > check_interval_seconds * settings.AGENT_STATUS_CHECK_OFFLINE_FACTOR:
        return AgentStatus.OFFLINE
    elif lateness > check_interval_seconds * settings.AGENT_STATUS_CHECK_UNHEALTHY_FACTOR:
        return AgentStatus.UNHEALTHY
    else:
        return AgentStatus.ONLINE


def _update_agent_status(agent: Agent, status: AgentStatus) -> bool:
    """'Atomically' update a given agent instance status without changing the instance itself."""
    count = (
        Agent.update(status=status)
        .where(
            Agent.id == agent.id,
            # Adding the latest_heartbeat timestamp to the 'where' clause to prevent the race condition where we
            # have just received a heartbeat for an agent that is about to having its status degraded.
            Agent.latest_heartbeat == agent.latest_heartbeat,
        )
        .execute()
    )
    return bool(count == 1)


class AgentStatusScheduleSource(ScheduleSource):
    source_name = "agent_status"
    kafka_topic = TOPIC_IDENTIFIED_EVENTS

    def _get_schedules(self) -> Select:
        return Project.select().where(Project.agent_check_interval > 0)

    def _create_and_add_job(self, schedule: Project) -> None:
        self.add_job(
            self._check_agents_are_online,
            str(schedule.id),
            IntervalTrigger(seconds=schedule.agent_check_interval),
            {"project": schedule},
        )

    def _check_agents_are_online(self, project: Project) -> None:
        check_threshold = datetime.now(tz=timezone.utc) - timedelta(seconds=project.agent_check_interval)
        for agent in Agent.select().where(
            Agent.project == project.id,
            Agent.latest_heartbeat < check_threshold,
        ):
            new_status = _get_agent_status(project.agent_check_interval, agent.latest_heartbeat)
            if agent.status == new_status:
                LOG.debug("Agent '%s' status did not change: %s", agent.id, agent.status)
            else:
                LOG.info("Agent '%s' status changed from %s to %s", agent.id, agent.status, new_status)
                if _update_agent_status(agent, new_status) and new_status == AgentStatus.OFFLINE:
                    self._send_agent_status_change_event(agent, new_status)

    def _send_agent_status_change_event(self, agent: Agent, new_status: AgentStatus) -> None:
        event = AgentStatusChangeEvent(
            project_id=agent.project_id,
            agent_id=agent.id,
            agent_key=agent.key,
            agent_tool=agent.tool,
            previous_status=agent.status,
            current_status=new_status,
            latest_heartbeat=agent.latest_heartbeat,
            latest_event_timestamp=agent.latest_event_timestamp,
        )

        with self.event_producer as producer:
            producer.produce(self.kafka_topic, event)
