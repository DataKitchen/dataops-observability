import { Optional, ReadonlyKeys } from 'utility-types';
import { EntityType } from './entity-type';

export interface SortOptions {
  sort_by?: any;
  sort?: 'asc' | 'desc' | '';
}

export interface Pagination {
  page?: number;
  count?: number;
}

export type Optionalize<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type withId<E extends WithId> = {
  id: E['id'];
} & Optional<E & object>;

export interface WithId {
  readonly id: string;
}

export interface Entity extends WithId {
  name: string;
  description: string;

  // readonly fields are never set from the UI
  // this allows us to exclude them from `TypedForms` with the `getFormFields` utility type
  readonly created_on: string;
  readonly created_by: {
    id: string;
    name: string;
  };
  readonly active: boolean;
}

export enum EntityPermission {
  Create = 'CREATE_CHILDREN',
  Update = 'UPDATE',
  Read = 'READ',
  List = 'LIST_CHILDREN',
  Deactivate = 'DEACTIVATE',
  Assign = 'ASSIGN',
}

export interface Role extends Entity {
  organization_id: number;
  system_role: boolean;
  permissions: { [entityType in EntityType]?: EntityPermission[] };
}

export type EntityListResponse<T> = {
  total: number;
  entities: T[];
};

export interface RequestOptions<SearchField = any> {
  filters?: SearchField;
  parentId?: string;
}

export type FindAllRequest<SearchFields = any> = RequestOptions<SearchFields> & SortOptions;

export type PaginatedRequest<SearchFields = any> = FindAllRequest<SearchFields> & Pagination;

export type nonReadonlyFields<T extends object> = Omit<T, ReadonlyKeys<T>> & { id?: string };
