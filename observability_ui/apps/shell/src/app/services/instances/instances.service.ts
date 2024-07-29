import { HttpClient } from '@angular/common/http';
import { Injectable, Optional } from '@angular/core';
import { BaseComponent, ConfigService, EntityListResponse, EntityService, EntityType, Instance, InstanceDag, InstancesSearchFields, UpcomingInstance, UpcomingInstancesSearchFields } from '@observability-ui/core';
import { Observable, of, switchMap } from 'rxjs';
import { JourneysService } from '../journeys/journeys.service';


@Injectable({
  providedIn: 'root'
})
export class InstancesService extends EntityService<Instance, InstancesSearchFields> {
  protected override baseEntity: EntityType = EntityType.Instance;
  protected override parentEntity = EntityType.Project;

  constructor(
    protected override config: ConfigService,
    protected override http: HttpClient,
    @Optional() private journeyService: JourneysService, // TODO: Remove once we have a components-by-instance API endpoint -- Here for easier refactoring
  ) {
    super(config, http);
  }

  /* istanbul ignore next */
  getComponents(journeyId: string): Observable<EntityListResponse<BaseComponent>> {
    return this.journeyService.getComponentsByJourney(journeyId);
  }

  getDag(instanceId: string): Observable<InstanceDag> {
    return this.http.get<InstanceDag>(`${this.getUrl()}/${ instanceId }/dag`);
  }

  getOrganizationInstances(filters: InstancesSearchFields): Observable<EntityListResponse<Instance>> {
    return this.findAll({ filters });
  }

  findUpcomingInstances(params: UpcomingInstancesSearchFields) {

    const url = `${this.config.get('apiBaseUrl')}/observability/v1/upcoming-instances`;

    const count = 50;

    return this.http.get<EntityListResponse<UpcomingInstance>>(url, {
      params: {
        ...params,
        count,
      },
    }).pipe(
      switchMap((response) => {
        if (response.total > count) {
          return this.http.get<EntityListResponse<UpcomingInstance>>(url, {
            params: {
              ...params,
              count: response.total,
            },
          });
        }

        return of(response);
      })
    );
  }
}
