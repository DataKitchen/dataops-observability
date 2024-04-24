import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of, switchMap } from 'rxjs';
import { ConfigService } from '../config/config.service';
import { EntityListResponse, FindAllRequest, PaginatedRequest } from './entity.model';
import { EntityType } from './entity-type';
import { entityDefaultUrlMappings } from './entity-default-url.mappings';


/**
 *   E is the entity model
 *
 */
@Injectable({
  providedIn: 'root'
})
export abstract class ReadOnlyRestApiService<E, SearchFields extends Record<string, any> = {}> {
  protected abstract readonly baseEntity: string;

  protected path = 'v1';
  protected prefix = 'observability';

  protected readonly parentEntity?: EntityType;

  entityTypeToUrlPart = entityDefaultUrlMappings;

  public apiBaseUrl: string = this.config.get('apiBaseUrl') as string;

  constructor(
    protected config: ConfigService,
    protected http: HttpClient,
  ) {
  }

  findAll({ parentId, filters, sort = '', ...request }: FindAllRequest<SearchFields> = {}) {
    const params = { ...request, ...filters, sort };
    return this.http.get<EntityListResponse<E>>(this.getUrl(parentId), {
      params: { ...params, count: 0 }
    }).pipe(
      switchMap((resp) => {
        if (resp.total > 0) {

          return this.http.get<EntityListResponse<E>>(this.getUrl(parentId), {
            params: { ...params, count: resp.total },
          });
        }

        return of(resp);
      }),
    );
  }

  getPage({ parentId, ...request }: PaginatedRequest) {
    const params = this.parsePaginationParams(request);
    return this.http.get<EntityListResponse<E>>(this.getUrl(parentId), { params });
  }

  getOne(id: string, params?: HttpParams): Observable<E> {
    return this.http.get<E>(`${this.getUrl()}/${id}`, { params });
  }

  protected getBaseUrl() {
    return `${this.apiBaseUrl}/${this.prefix}/${this.path}`;
  }

  protected getUrl(parentId?: string): string {

    if (!!this.parentEntity && !!parentId) {
      return `${this.getBaseUrl()}/${this.entityTypeToUrlPart[this.parentEntity]}/${parentId}/${this.entityTypeToUrlPart[this.baseEntity]}`;
    }

    return `${this.getBaseUrl()}/${this.entityTypeToUrlPart[this.baseEntity]}`;
  }

  protected parsePaginationParams({
                                    page,
                                    count = 0,
                                    filters = {},
                                    sort = '',
                                    ...request
                                  }: Omit<PaginatedRequest, 'parentId'>) {
    const sortOptions = sort?.toUpperCase();
    return { ...request, ...filters, sort: sortOptions, count, page: (page as number || 0) + 1 };
  }

}
