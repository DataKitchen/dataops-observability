import { Injectable } from '@angular/core';
import { EntityActions, EntityState, EntityStore, RunTask } from '@observability-ui/core';
import { RunTasksService } from '../../services/run-tasks/run-tasks.service';
import { makeStore } from '@microphi/store';

@Injectable({
  providedIn: 'root'
})
/**
 * TODO this should be under the RunStore
 */
export class RunTasksStore extends EntityStore<EntityState<RunTask>, EntityActions<RunTask>> implements makeStore<EntityState<RunTask>, EntityActions<RunTask>> {

  constructor(protected service: RunTasksService) {
    super({
      total: 0,
      list: []
    });
  }
}
