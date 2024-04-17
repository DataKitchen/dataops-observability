import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { BaseComponent, ComponentType, ConfigService, withId } from '@observability-ui/core';


@Injectable({
  providedIn: 'root'
})
export abstract class BaseComponentService<E extends BaseComponent> {
  protected abstract readonly type: ComponentType;

  protected apiBaseUrl: string = this.config.get('apiBaseUrl') as string;

  protected readonly componentTypeToUrlPart: { [ type in ComponentType ]?: string } = {
    [ComponentType.BatchPipeline]: 'batch-pipelines',
    [ComponentType.Dataset]: 'datasets',
    [ComponentType.StreamingPipeline]: 'streaming-pipelines',
    [ComponentType.Server]: 'servers'
  };

  constructor(
    protected config: ConfigService,
    protected http: HttpClient,
  ) { }

  getOne(id: string): Observable<E> {
    return this.http.get<E>(`${this.apiBaseUrl}/observability/v1/${this.componentTypeToUrlPart[this.type]}/${id}`);
  }

  update({id, type, ...entity}: withId<E>): Observable<E> {
    return this.http.patch<E>(`${this.apiBaseUrl}/observability/v1/${this.componentTypeToUrlPart[type]}/${id}`, entity);
  }

  delete(id: string): Observable<{ id: string }> {
    return this.http.delete(`${this.apiBaseUrl}/observability/v1/components/${id}`).pipe(
      map(() => ({id})),
    );
  }
}
