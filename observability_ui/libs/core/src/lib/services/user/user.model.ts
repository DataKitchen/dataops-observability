import { Entity, EntityType, Role } from '../../entity';
import { Company } from '../company/company.model';

export interface User extends Entity {
  email: string;
  job_title: string;
  job_function: string;
  primary_company: string;
  admin: boolean;
  roles?: UserRoleAssignment[];
}

export interface ExpandedUser extends Omit<User, 'primary_company' | 'created_by'> {
  created_by: User;
  primary_company: Company;
}

export interface UserRoleAssignment extends Role {
  assignments: { [entityType in EntityType]?: number[] };
}
