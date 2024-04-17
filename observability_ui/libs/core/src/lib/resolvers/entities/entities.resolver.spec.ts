import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { Company } from '../../services/company/company.model';
import { CompanyService } from '../../services/company/company.service';
import { Organization } from '../../services/organization/organization.model';
import { OrganizationService } from '../../services/organization/organization.service';
import { Project } from '../../services/project/project.model';
import { ProjectService } from '../../services/project/project.service';
import { EntitiesResolver } from './entities.resolver';
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import { MockProvider } from '@datakitchen/ngx-toolkit';

describe('EntitiesResolver', () => {
  const companyId = '1';
  const company = {id: companyId} as Company;
  const organizationId = '15';
  const organization = {id: organizationId, company: companyId} as Organization;
  const organizations = [ organization ];
  const projectId = '1241';
  const project = {id: projectId, organization: organizationId} as Project;
  const projects = [ project ];

  let resolver: EntitiesResolver;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        EntitiesResolver,
        MockProvider(ProjectService, class {
          getOne = jest.fn().mockReturnValue(of(project));
          findAll = jest.fn().mockReturnValue(of({entities: projects}));
        }),
        MockProvider(OrganizationService, class {
          getOne = jest.fn().mockReturnValue(of(organization));
          findAll = jest.fn().mockReturnValue(of({entities: organizations}));
        }),
        MockProvider(CompanyService, class {
          getOne = jest.fn().mockReturnValue(of(company));
        }),
      ],
    });

    resolver = TestBed.inject(EntitiesResolver);
  });

  it('should create', () => {
    expect(resolver).toBeDefined();
  });


  describe('#resolveEntitites', () => {

    it('should call BE to resolve entities', () => {
      TestScheduler.expect$(resolver.resolveEntities('companyId')).toContain({
        company,
        organizations,
      });
    });

    describe('reduce state', () => {


      it('should set (over default) state', () => {
        expect(resolver.onResolveEntities({
          organization: undefined,
          organizations: undefined,
          company: undefined,
        }, {company, organizations})).toEqual({
          organizations,
          organization: organizations[0],
          company,
        });

      });

      it('should set the state (project and organization already set)', () => {
        expect(resolver.onResolveEntities({
          organization: {id: 'org_id'} as Organization,
          organizations: undefined,
          company: undefined,
        }, {company, organizations})).toEqual({
          organizations,
          organization: {id: 'org_id'} as Organization,
          company,
        });
      });

    });

  });


});
