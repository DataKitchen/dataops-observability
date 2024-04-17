import { Injectable } from '@angular/core';
import { User } from './user.model';
import { Observable } from 'rxjs';
import { EntityListResponse, EntityService, EntityType } from '../../entity';

@Injectable({
  providedIn: 'root'
})
export class UserService extends EntityService<User> {

  override baseEntity = EntityType.User;

  getUsersByCompany(companyId: number): Observable<EntityListResponse<User>> {
    return this.http.get<EntityListResponse<User>>(`${this.apiBaseUrl}/${this.prefix}/v1/companies/${companyId}/users`);
  }

}
