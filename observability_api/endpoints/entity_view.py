import logging
from typing import cast

from peewee import DoesNotExist, IntegrityError, ModelSelect
from werkzeug.exceptions import Conflict, Forbidden, NotFound

from common.api.base_view import BaseView
from common.entities import BaseEntity, Company, Project
from common.join_helpers import join_until

LOG = logging.getLogger(__name__)


class BaseEntityView(BaseView):
    root_entity: type[BaseEntity] = Company

    def apply_membership(self, query: ModelSelect) -> ModelSelect:
        if self.user:
            if self.user.admin:
                return query
            else:
                return query.where(Company.id == self.user.primary_company_id)
        elif self.project:
            return query.where(Project.id == self.project)
        else:
            raise Forbidden()

    def get_entity_from_query_or_fail(self, query: ModelSelect) -> BaseEntity:
        base_query = join_until(query, self.root_entity)
        membership_query = self.apply_membership(base_query)

        try:
            return cast(BaseEntity, membership_query.get())
        except DoesNotExist:
            try:
                base_query.get()
            except DoesNotExist as dne:
                raise NotFound(f"The requested {base_query.model.__name__} does not exist.") from dne
            else:
                raise Forbidden()

    def get_entity_or_fail(self, entity_class: type[BaseEntity], *where: object) -> BaseEntity:
        return self.get_entity_from_query_or_fail(entity_class.select().where(*where))

    @staticmethod
    def save_entity_or_fail(entity: BaseEntity, force_insert: bool = False) -> None:
        try:
            entity.save(force_insert=force_insert)
        except IntegrityError as e:
            LOG.exception("Failed to create/update %s ID", entity.__class__.__name__)
            raise Conflict(
                f"Failed to create/update {entity.__class__.__name__}; one already exists with that information"
            ) from e
