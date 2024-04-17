import { Injectable } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ConfigService } from '../config/config.service';
import { EntityService } from './entity.service';
import { Entity } from './entity.model';
import { EntityType } from './entity-type';

describe('EntityService', () => {


  interface Ent extends Entity {
    entityField1: string;
  }

  @Injectable()
  class TestService extends EntityService<Ent> {
    protected readonly baseEntity: EntityType = EntityType.Organization;
    protected override readonly parentEntity: EntityType | undefined = EntityType.Company;
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


  describe('create', () => {
    it('should call create api endpoint with correct params', (done) => {
      const expected = {
        id: '1'
      } as Ent;

      service.create(expected).subscribe((resp) => {
        expect(resp).toEqual(expected);
        done();
      });

      httpClient.expectOne('base/observability/v1/organizations').flush(expected);
    });
  });

  describe('update', () => {
    it('should call update api endpoint with correct params', (done) => {
      const expected = {
        id: '1'
      } as Ent;

      service.update(expected).subscribe((resp) => {
        expect(resp).toEqual(expected);
        done();
      });

      httpClient.expectOne('base/observability/v1/organizations/1').flush(expected);
    });
  });
});
