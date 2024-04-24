import { Injectable } from '@angular/core';
import { EntityListResponse, EntityService, EntityType, FindAllRequest, RunTask } from '@observability-ui/core';
import { HttpParams } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
/**
 * TODO: this endpoint is not rest and it should be under the run endpoint
 */
export class RunTasksService extends EntityService<RunTask> {
  protected override parentEntity = EntityType.Run;
  protected override baseEntity = EntityType.Task;

  override findAll({ parentId, ...request }: FindAllRequest = {}) {
    const params = { ...request } as HttpParams;
    return this.http.get<EntityListResponse<RunTask>>(this.getUrl(parentId), {
      params,
    });
  }
}
