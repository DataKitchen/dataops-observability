import { Injectable } from '@angular/core';
import { BaseComponent, ComponentType, EntityListResponse, EntityService, EntityType, nonReadonlyFields, Schedule } from '@observability-ui/core';
import { map, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ComponentsService extends EntityService<BaseComponent> {
  protected override baseEntity: string = EntityType.Component;
  protected override parentEntity = EntityType.Project;

  override entityTypeToUrlPart = {
    [ComponentType.BatchPipeline]: 'batch-pipelines',
    [ComponentType.Dataset]: 'datasets',
    [ComponentType.StreamingPipeline]: 'streaming-pipelines',
    [ComponentType.Server]: 'servers',
    [EntityType.Component]: 'components',
    [EntityType.Project]: 'projects',
    [EntityType.Dashboards]: 'dashboards'
  };

  override create(component: nonReadonlyFields<BaseComponent>, parentId: string): Observable<BaseComponent> {

    this.baseEntity = component.type;

    return super.create(component, parentId);
  }

  /**
   * although the response is of type `EntityListResponse` at the moment we can have only
   * two type of response:
   *
   *
   *  When the component is of type `BatchPipeline`
   *  We can have an array with maximum two schedules
   *  one with the field `expectation` is set to `BATCH_PIPELINE_START_TIME`
   *  and another one set to `BATCH_PIPELINE_END_TIME`
   *
   *  The following rules apply:
   *
   *  - Both elements are optional
   *  - `BATCH_PIPELINE_START_TIME` has the `margin` field set which is a number that express the time in minutes
   *    - margin must be greater than 0
   *  - `BATCH_PIPELINE_END_TIME` does have the `margin` field
   *
   *
   *  When the component is for type `Dataset`
   *  We can have an array with one element with the field `expectation` set to `DATASET_ARRIVAL`
   *  The following rules apply:
   *
   *   - the element is optional
   *   - the schedule and the margin fields are both required
   *   - margin should be at least 5
   *
   * @param id the component id
   */
  getSchedules(id: string): Observable<EntityListResponse<Schedule>> {
    return this.http.get<EntityListResponse<Schedule>>(`${this.apiBaseUrl}/observability/v1/components/${id}/schedules`);
  }

  createSchedule(id: string, schedule: Partial<Schedule>): Observable<Schedule> {
    return this.http.post<Schedule>(`${this.apiBaseUrl}/observability/v1/components/${id}/schedules`, schedule);
  }

  deleteSchedule(scheduleId: string): Observable<any> {
    return this.http.delete(`${this.apiBaseUrl}/observability/v1/schedules/${scheduleId}`);
  }

  override delete(id: string): Observable<{ id: string }> {
    return this.http.delete(`${this.apiBaseUrl}/observability/v1/components/${id}`).pipe(
      map(() => {
        return { id };
      })
    );
  }

  override update({ id, name, description, tool, type }: BaseComponent, parentId?: string): Observable<BaseComponent> {

    this.baseEntity = type;

    return this.http.patch<BaseComponent>(`${this.getUrl(parentId)}/${id}`, {
      name, description, tool,
    });
  }


  override getUrl(parentId?: string): string {
    const url = super.getUrl(parentId);
    // reset baseEntity for next call
    this.baseEntity = EntityType.Component;

    return url;
  }

}
