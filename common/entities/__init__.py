"""Any new model that's added should also be added here"""

from .action import *
from .agent import *
from .alert import *
from .auth_provider import *
from .authentication import *
from .base_entity import *
from .company import *
from .component import *
from .dataset import *
from .dataset_operation import *
from .event import *
from .instance import *
from .instance_rule import *
from .journey import *
from .organization import *
from .pipeline import *
from .project import *
from .rule import *
from .run import *
from .schedule import *
from .server import *
from .streaming_pipeline import *
from .task import *
from .test_outcome import *
from .testgen import *
from .upcoming_instance import *
from .user import *

# The list of all Models that can have Permissions applied to them in the RBAC system
PERMISSIONED_MODELS: list[type[BaseEntity]] = [Company, Organization, Project, User]
ALL_MODELS: list[type[BaseEntity]] = [
    *PERMISSIONED_MODELS,
    Action,
    Agent,
    ApiKey,
    AuthProvider,
    Component,
    Dataset,
    DatasetOperation,
    EventEntity,
    Instance,
    InstanceAlert,
    InstanceAlertsComponents,
    InstanceRule,
    InstanceSet,
    InstancesInstanceSets,
    Journey,
    JourneyDagEdge,
    Pipeline,
    Role,
    Rule,
    Run,
    RunAlert,
    RunTask,
    Schedule,
    Server,
    ServiceAccountKey,
    StreamingPipeline,
    Task,
    TestgenDatasetComponent,
    TestGenTestOutcomeIntegration,
    TestOutcome,
    UserRole,
]
