import { Injectable } from '@angular/core';
import { filter, forkJoin, map, Observable } from 'rxjs';
import { Company, CompanyService, Organization, OrganizationService } from '../../services';
import { Effect, makeStore, Reduce, Store } from '@microphi/store';

interface EntitiesResolverState {
  organization: Organization | undefined;
  company: Company | undefined;
  organizations: Organization[] | undefined;
}


interface EntitiesResolverActions {
  resolveEntities: (companyId: string) => Observable<{
    company: Company,
    organizations: Organization[],
  }>;

  getOrganization: (id: string) => Observable<Organization>;
  getOrganizations: (companyId: string) => Observable<Organization[]>;
  getCompany: (id: string) => Observable<Company>;
}

@Injectable({providedIn: 'root'})
export class EntitiesResolver extends Store<EntitiesResolverState, EntitiesResolverActions> implements makeStore<EntitiesResolverState, EntitiesResolverActions> {

  company$ = this.select(state => state.company);
  organization$ = this.select(state => state.organization).pipe(
    filter(Boolean)
  );
  organizations$ = this.select(state => state.organizations);


  constructor(
    private organizationServices: OrganizationService,
    private companyService: CompanyService,
  ) {
    super({
      company: undefined,
      organization: undefined,
      organizations: [],
    });
  }



  @Effect()
  getOrganization(id: string): Observable<Organization> {
    return this.organizationServices.getOne(id);
  }

  @Reduce()
  onGetOrganization(state: EntitiesResolverState, organization: Organization): EntitiesResolverState {
    return {
      ...state,
      organization,
    };
  }

  @Effect()
  getCompany(id: string): Observable<Company> {
    return this.companyService.getOne(id);
  }

  @Reduce()
  onGetCompany(state: EntitiesResolverState, company: Company): EntitiesResolverState {
    return {
      ...state,
      company,
    };
  }

  @Effect()
  getOrganizations(companyId: string): Observable<Organization[]> {
    return this.organizationServices.findAll({parentId: companyId}).pipe(
      map(({entities}) => entities as Organization[])
    );
  }

  @Reduce()
  onGetOrganizations(state: EntitiesResolverState, organizations: Organization[]): EntitiesResolverState {
    return {
      ...state,
      organizations,
      organization: state.organization || organizations[0]
    };
  }


  @Effect()
  resolveEntities(companyId: string): Observable<{ company: Company; organizations: Organization[]; }> {
    return forkJoin([
      this.companyService.getOne(companyId),
      this.getOrganizations(companyId),
    ]).pipe(
      map(([ company,  organizations]) => {
        return {
          company,
          organizations,
        };
      })
    );
  }

  @Reduce()
  onResolveEntities(state: EntitiesResolverState, payload: { company: Company; organizations: Organization[]; }): EntitiesResolverState {

    const {organizations, organization} = this.onGetOrganizations(state, payload.organizations);

    return {
      company: payload.company,
      organization,
      organizations,
    };
  }

}

