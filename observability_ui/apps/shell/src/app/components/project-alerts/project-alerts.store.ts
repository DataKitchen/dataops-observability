import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Effect, makeStore, Reduce, Store } from '@microphi/store';
import { ProjectAlertSettings, ProjectService} from "@observability-ui/core";


export interface ProjectAlertSettingsState {
  alertSettings: ProjectAlertSettings;
}

interface ProjectAlertSettingsActions {
  get: (projectId: string) => Observable<ProjectAlertSettings>;
  update: (projectId: string, alertSettings: ProjectAlertSettings) => Observable<ProjectAlertSettings>;
}

@Injectable({providedIn: 'root'})
export class ProjectAlertSettingsStore
  extends Store<ProjectAlertSettingsState, ProjectAlertSettingsActions>
  implements makeStore<ProjectAlertSettingsState, ProjectAlertSettingsActions>
{

  constructor(projectService: ProjectService) {
    super({
      alertSettings: {
        agent_check_interval: undefined,
        actions: [],
      }
    });
    this.service = projectService;
  }

  protected service: ProjectService;

  alertSettings$ = this.select(state => state.alertSettings);

  @Effect()
  get(projectId: string): Observable<ProjectAlertSettings> {
    return this.service.getAlertSettings(projectId);
  }

  @Reduce()
  onGet(state: ProjectAlertSettingsState, payload: ProjectAlertSettings): ProjectAlertSettingsState {
    if (payload) {
      return { alertSettings: payload };
    } else {
      return state;
    }
  }

  @Effect()
  update(projectId: string, alertSettings: ProjectAlertSettings): Observable<ProjectAlertSettings> {
    return this.service.updateAlertSettings(projectId, alertSettings);
  }

  @Reduce()
  onUpdate(state: ProjectAlertSettingsState, payload: ProjectAlertSettings): ProjectAlertSettingsState {
    if (payload) {
      return { alertSettings: payload };
    } else {
      return state;
    }
  }
}
