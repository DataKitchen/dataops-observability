import { TestBed } from '@angular/core/testing';
import { ReadOnlyRestApiService } from './read-only-rest-api.service';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ConfigService } from '../config/config.service';
import { Injectable } from '@angular/core';

import { EntityType } from './entity-type';

describe('RestApiService', () => {


  @Injectable()
  class TestService extends ReadOnlyRestApiService<{ id: string }> {
    protected readonly baseEntity = EntityType.Company;
    override prefix = 'tests';
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

  it('should call GET endpoint for list of entities ', (done) => {

    const expected = {
      entities: [{id: 'a'}],
      total: 1,
    };

    service.findAll().subscribe((resp) => {
      expect(resp).toEqual(expected);
      done();
    });


    const request1 = httpClient.expectOne('base/tests/v1/companies?sort=&count=0');
    request1.flush({
      entities: [],
      total: 1,
    });

    const request2 = httpClient.expectOne('base/tests/v1/companies?sort=&count=1');
    request2.flush(expected);
  });

  it('should get a page', (done) => {

    const expected = {
      entities: [],
      count: 1,
    };

    service.getPage({
      page: 0,
      count: 10,
    }).subscribe((resp) => {
      expect(resp).toEqual({
        ...expected,
      });
      done();
    });

    const request = httpClient.expectOne(`base/tests/v1/companies?sort=&count=10&page=1`);
    request.flush(expected);
  });

  it('should get an entity', (done) => {

    const expected = {
      id: '1'
    };

    service.getOne('1').subscribe((resp) => {
      expect(resp).toEqual(expected);
      done();
    });

    const request = httpClient.expectOne(`base/tests/v1/companies/1`);
    request.flush(expected);
  });

});
