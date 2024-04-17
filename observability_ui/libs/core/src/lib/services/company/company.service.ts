import { Injectable } from '@angular/core';
import { Action, ActionsSearchFields, Company } from './company.model';
import { EntityListResponse, EntityService, EntityType, PaginatedRequest } from '../../entity';

@Injectable({ providedIn: 'root' })
export class CompanyService extends EntityService<Company> {
  protected override baseEntity = EntityType.Company;

  getActions({ parentId, ...request }: PaginatedRequest<ActionsSearchFields> = {}) {
    const params = this.parsePaginationParams(request);
    const url = `${this.getUrl()}/${parentId}/actions`;
    return this.http.get<EntityListResponse<Action>>(url, { params });
  }

  updateAction({ id, ...payload }: Action) {
    const url = `${this.apiBaseUrl}/observability/v1/actions/${id}`;
    return this.http.patch<Action>(url, payload);
  }
}
