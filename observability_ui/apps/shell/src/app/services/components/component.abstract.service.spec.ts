import { Injectable } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { BaseComponent, ComponentType, ConfigService } from '@observability-ui/core';
import { BaseComponentService } from './component.abstract.service';

describe('BaseComponentService', () => {


  interface Ent extends BaseComponent {
    entityField1: string;
  }

  @Injectable()
  class TestService extends BaseComponentService<Ent> {
    protected override type: ComponentType = ComponentType.BatchPipeline;
  }

  let service: TestService;
  let httpClient: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ HttpClientTestingModule ],
      providers: [
        TestService,
        {
          provide: ConfigService,
          useClass: class {
            get = () => 'base';
          }
        },
      ]
    });

    httpClient = TestBed.inject(HttpTestingController);
    service = TestBed.inject(TestService);

  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('getOne', () => {
    it('should get an entity', (done) => {
      const expected = {
        id: '1'
      };

      service.getOne('1').subscribe((resp) => {
        expect(resp).toEqual(expected);
        done();
      });

      httpClient.expectOne({
        method: 'GET',
        url: 'base/observability/v1/batch-pipelines/1',
      }).flush(expected);
    });
  });

  describe('update', () => {
    it('should call update api endpoint with correct params', (done) => {
      const expected = {
        id: '1',
        type: ComponentType.BatchPipeline,
      } as Ent;

      service.update(expected).subscribe((resp) => {
        expect(resp).toEqual(expected);
        done();
      });

      httpClient.expectOne({
        method: 'PATCH',
        url: 'base/observability/v1/batch-pipelines/1',
      }).flush(expected);
    });
  });

  describe('delete', () => {
    it('should call delete api endpoint with correct params', (done) => {
      service.delete('1').subscribe((resp) => {
        expect(resp).toEqual({ id: '1' });
        done();
      });

      httpClient.expectOne({
        method: 'DELETE',
        url: 'base/observability/v1/components/1',
      }).flush({});
    });
  });
});
