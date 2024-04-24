import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ConfigService } from '../../config/config.service';
import { OrganizationService } from './organization.service';

describe('OrganizationService', () => {
  let organizationService: OrganizationService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ HttpClientTestingModule ],
      declarations: [],
      providers: [
        OrganizationService,
        {
          provide: ConfigService,
          useClass: class {
            get = () => 'base';
          }
        },
      ]
    });

    organizationService = TestBed.inject(OrganizationService);
  });

  it('should create', () => {
    expect(organizationService).toBeDefined();
  });
});
