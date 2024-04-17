"""
The 'schemas' module contains the "middleware" models for Observability, utilizing Marshmallow.

The goal here is to cleanly define the schemas to be used in the API for (de)serialization, and for
auto-generating an API Spec document for Swagger.
"""
from .action_schemas import *
from .agent_schemas import *
from .alert_schemas import *
from .base_schemas import *
from .company_schemas import *
from .component_schemas import *
from .dataset_schemas import *
from .event_schemas import *
from .instance_rule_schemas import *
from .instance_schemas import *
from .journey_dag_schemas import *
from .journey_schemas import *
from .organization_schemas import *
from .pipeline_schemas import *
from .project_schemas import *
from .rule_schemas import *
from .run_schemas import *
from .schedule_schemas import *
from .server_schemas import *
from .service_account_key_schemas import *
from .streaming_pipeline_schemas import *
from .task_schemas import *
from .testgen_dataset_component_schemas import *
from .testgen_test_outcome_schemas import *
from .upcoming_instance_schemas import *
from .user_schemas import *

# Not all schemas are included in the list below because they are
# implicitly included and generate warnings if included again.
# Excluded schemas:
# RunSummarySchema,
# TestOutcomeSummarySchema,
# TestgenDatasetComponentSchema,
# WebhookActionArgsSchema,
ALL_SCHEMAS = [
    ActionSchema,
    AgentSchema,
    CallWebhookRuleSchema,
    CompanyPatchSchema,
    CompanySchema,
    ComponentPatchSchema,
    ComponentSchema,
    DatasetSchema,
    EmailActionArgsSchema,
    EventResponseSchema,
    InstanceAlertSchema,
    InstanceDetailedSchema,
    InstanceRulePostSchema,
    InstanceRuleSchema,
    InstanceSchema,
    JourneyDagEdgePostSchema,
    JourneyDagEdgeSchema,
    JourneyDagNodeSchema,
    JourneyDagSchema,
    JourneyPatchSchema,
    JourneySchema,
    OrganizationPatchSchema,
    OrganizationSchema,
    PipelineSchema,
    ProjectPatchSchema,
    ProjectSchema,
    RulePatchCallWebhookSchema,
    RulePatchSchema,
    RulePatchSendEmailSchema,
    RuleSchema,
    RunAlertSchema,
    RunSchema,
    RunTaskSchema,
    ScheduleSchema,
    SendEmailRuleSchema,
    ServerSchema,
    ServiceAccountKeyCreateSchema,
    ServiceAccountKeySchema,
    ServiceAccountKeyTokenSchema,
    StreamingPipelineSchema,
    TaskSchema,
    TestOutcomeItemSchema,
    UpcomingInstanceSchema,
    UserPatchSchema,
    UserSchema,
]
