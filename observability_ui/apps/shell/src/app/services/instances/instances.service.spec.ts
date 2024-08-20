import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ConfigService, InstanceDag, InstancesSearchFields } from '@observability-ui/core';
import { InstancesService } from './instances.service';

describe('Instances Service', () => {
  let service: InstancesService;
  let httpClient: HttpTestingController;

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
    httpClient = TestBed.inject(HttpTestingController);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('getDag()', () => {
    it('should fetch the DAG nodes from the server', (done) => {
      const dag: InstanceDag = {nodes: []};

      service.getDag('123').subscribe((response) => {
        expect(response).toEqual(dag);
        done();
      });

      httpClient.expectOne('base/observability/v1/instances/123/dag').flush(dag);
    });
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
