__all__ = ["PipelineService"]
import logging
from typing import Optional

from common.entities import Pipeline

LOG = logging.getLogger(__name__)


class PipelineService:
    @staticmethod
    def get_by_key_and_project(pipeline_key: Optional[str], project_id: str) -> Pipeline:
        pipeline: Pipeline = Pipeline.get(Pipeline.key == pipeline_key, Pipeline.project == project_id)
        return pipeline
