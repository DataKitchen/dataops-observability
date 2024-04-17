import { Injectable } from '@angular/core';
import { BaseComponent, ComponentType, EntityListResponse, EntityService, EntityType, Journey, JourneyDag, JourneyInstanceRule, withId } from '@observability-ui/core';
import { catchError, mapTo, Observable, of, switchMap } from 'rxjs';
import { omit } from '@datakitchen/ngx-toolkit';

@Injectable({
  providedIn: 'root'
})
export class JourneysService extends EntityService<Journey> {
  protected override baseEntity: EntityType = EntityType.Journey;
  protected override parentEntity = EntityType.Project;

  override create(entity: Partial<Journey>, parentId?: string | undefined): Observable<Journey> {
      return super.create(omit(entity, [ 'instance_rules' ]), parentId);
  }

  override update({ id, ...entity }: withId<Journey>, parentId?: string | undefined): Observable<Journey> {
      return super.update({ id, ...omit(entity, [ 'instance_rules' ]) }, parentId);
  }

  /* istanbul ignore next */
  createInstanceRule(journeyId: string, {action, batch_pipeline, schedule}: Omit<JourneyInstanceRule, 'id'>): Observable<JourneyInstanceRule> {
    return this.http.post<JourneyInstanceRule>(`${this.getUrl()}/${ journeyId }/instance-conditions`,  {
      action,
      batch_pipeline: batch_pipeline ?? undefined, // if null we need to make undefined so BE doesn't cry 😢
      // same here 👇
      schedule: schedule ? { expression: schedule.schedule, timezone: schedule.timezone } as any : undefined,
    }).pipe(
      switchMap((rule) => {

        if (rule.batch_pipeline) {
          return this.createJourneyDagEdge(journeyId, undefined, rule.batch_pipeline).pipe(
            mapTo(rule),
            catchError((error) => {
              console.log(error);
              return of(rule);
            }),
          );
        } else {
          return of(rule);
        }
      })
    );
  }

  deleteInstanceRule(id: string): Observable<any> {
    return this.http.delete(`${this.apiBaseUrl}/observability/v1/instance-conditions/${id}`);
  }

  getComponentsByJourney(id: string, filters: { component_type?: ComponentType[] } = {}): Observable<EntityListResponse<BaseComponent>> {
    const url = `${this.getUrl()}/${ id }/components`;
    return this.http.get<EntityListResponse<BaseComponent>>(url, {
      params: { ...filters, count: 0 }
    }).pipe(
      switchMap((resp) => {
        if (resp.total > 0) {

          return this.http.get<EntityListResponse<BaseComponent>>(url, {
            params: { ...filters, count: resp.total },
          });

        }

        return of(resp);
      }),
    );
  }

  getJourneyDag(id: string): Observable<JourneyDag> {
    return this.http.get<JourneyDag>(`${this.getUrl()}/${id}/dag`);
  }

  createJourneyDagEdge(journeyId: string, left: string | undefined, right: string): Observable<{ id: string; left: string | undefined; right: string }> {
    return this.http.put<{ id: string; left: string | undefined; right: string }>(`${this.getUrl()}/${journeyId}/dag`, { left, right });
  }

  deleteJourneyDagEdge(edgeId: string): Observable<void> {
    return this.http.delete<void>(`${this.apiBaseUrl}/${this.prefix}/v1/journey-dag-edge/${edgeId}`);
  }
}
