import { Injectable } from '@angular/core';
import { AlertsSearchFields, Project, ProjectAlertSettings, ServiceKey, TestsSearchFields } from './project.model';
import { EntityListResponse, EntityService, EntityType, FindAllRequest, PaginatedRequest } from '../../entity';
import { EventType, EventSearchFields, TestOutcomeItem } from '../../models/event.model';
import { Observable, of, switchMap } from 'rxjs';
import { InstanceAlert } from '../../models';

@Injectable({ providedIn: 'root' })
export class ProjectService extends EntityService<Project> {
  protected override baseEntity = EntityType.Project;
  protected override parentEntity = EntityType.Organization;

  getEvents({ parentId, ...request }: PaginatedRequest<EventSearchFields> = {}) {
    const params = this.parsePaginationParams(request);
    // `parentId` here is the project id
    const url = `${this.getUrl()}/${parentId}/events`;
    return this.http.get<EntityListResponse<EventType>>(url, { params });
  }

  getAllEvents(request: FindAllRequest<EventSearchFields> = {}): Observable<EntityListResponse<EventType>> {
    return this.getEvents({ ...request, count: 0 }).pipe(
      switchMap((resp) => {
        if (resp.total > 0) {
          return this.getEvents({ ...request, count: resp.total });
        }
        return of(resp);
      }),
    );
  }

  createServiceAccountKey(projecId: string, payload: {
    name: string;
    description?: string;
    expires_after_days: number;
    allowed_services: string[]
  }) {
    const url = `${this.getUrl()}/${projecId}/service-account-key`;
    return this.http.post<ServiceKey>(url, payload);
  }

  getServiceAccountKeys({ parentId, ...request }: PaginatedRequest<ServiceKey> = {}) {
    const params = this.parsePaginationParams(request);
    const url = `${this.getUrl()}/${parentId}/service-account-key`;
    return this.http.get<EntityListResponse<ServiceKey>>(url, { params });
  }

  getTestById(testId: string): Observable<TestOutcomeItem> {
    return this.http.get<TestOutcomeItem>(`${this.getBaseUrl()}/test-outcomes/${testId}`);
  }

  getTests({ parentId, ...request }: PaginatedRequest<TestsSearchFields> = {}) {
    const params = this.parsePaginationParams(request);

    const url = `${this.getUrl()}/${parentId}/tests`;
    return this.http.get<EntityListResponse<TestOutcomeItem>>(url, { params });
  }

  getAllTests(request: FindAllRequest<TestsSearchFields> = {}): Observable<EntityListResponse<TestOutcomeItem>> {
    return this.getTests({ ...request, count: 0 }).pipe(
      switchMap((resp) => {
        if (resp.total > 0) {
          return this.getTests({ ...request, count: resp.total });
        }
        return of(resp);
      }),
    );
  }

  getAlerts({ parentId, ...request }: PaginatedRequest<AlertsSearchFields> = {}) {
    const params = this.parsePaginationParams(request);

    const url = `${this.getUrl()}/${parentId}/alerts`;
    return this.http.get<EntityListResponse<InstanceAlert>>(url, { params });
  }

  getAlertSettings(projectId: string): Observable<ProjectAlertSettings> {
    return this.http.get<ProjectAlertSettings>(`${this.getUrl()}/${projectId}/alert-settings`);
  }

  updateAlertSettings(projectId: string, projectAlertSettings: ProjectAlertSettings): Observable<ProjectAlertSettings> {
    return this.http.patch<ProjectAlertSettings>(
      `${this.getUrl()}/${projectId}/alert-settings`,
      projectAlertSettings,
    );
  }
}
