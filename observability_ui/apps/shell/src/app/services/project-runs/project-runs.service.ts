import { Injectable } from '@angular/core';
import { EntityService, EntityType, Run } from '@observability-ui/core';

@Injectable({
  providedIn: 'root'
})
export class ProjectRunsService extends EntityService<Run> {
  protected override parentEntity = EntityType.Project;
  protected override baseEntity = EntityType.Run;
}
