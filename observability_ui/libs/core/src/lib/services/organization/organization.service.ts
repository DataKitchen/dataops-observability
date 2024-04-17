import { Injectable } from '@angular/core';
import { Organization } from './organization.model';
import { EntityService, EntityType } from '../../entity';

@Injectable({ providedIn: 'root' })
export class OrganizationService extends EntityService<Organization> {
  protected override baseEntity = EntityType.Organization;
  protected override parentEntity = EntityType.Company;
}
