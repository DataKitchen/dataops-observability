import { HttpClientTestingModule } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ConfigService, InstancesSearchFields } from '@observability-ui/core';
import { InstancesService } from './instances.service';

describe('Instances Service', () => {
  let service: InstancesService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ HttpClientTestingModule ],
      declarations: [],
      providers: [
        InstancesService,
        {
          provide: ConfigService,
          useClass: class {
            get = () => 'base';
          }
        },
      ]
    });

    service = TestBed.inject(InstancesService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('getOrganizationInstances', () => {
    it('should call findAll with filters', () => {
      service.findAll = jest.fn();

      const filters: InstancesSearchFields = {
        active: true
      };
      service.getOrganizationInstances(filters);
      expect(service.findAll).toHaveBeenCalledWith({ filters });
    });
  });
});
