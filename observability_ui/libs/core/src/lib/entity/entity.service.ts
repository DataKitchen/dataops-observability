import { Injectable } from '@angular/core';
import { WithId, withId } from './entity.model';
import { map, Observable } from 'rxjs';
import { ReadOnlyRestApiService } from './read-only-rest-api.service';


@Injectable({
  providedIn: 'root'
})
export abstract class EntityService<E extends WithId, SearchFields extends Record<string, any> = {}> extends ReadOnlyRestApiService<E, SearchFields> {

  create(entity: Partial<E>, parentId?: string): Observable<E> {
    return this.http.post<E>(this.getUrl(parentId), entity);
  }

  update({id, ...entity}: withId<E>, parentId?: string): Observable<E> {
    return this.http.patch<E>(`${this.getUrl(parentId)}/${id}`, entity);
  }

  delete(id: string, parentId?: string): Observable<{ id: string }> {
    return this.http.delete(`${this.getUrl(parentId)}/${id}`).pipe(
      // map to id so that in store we can remove the entity
      map(() => ({id})),
    );
  }
}
