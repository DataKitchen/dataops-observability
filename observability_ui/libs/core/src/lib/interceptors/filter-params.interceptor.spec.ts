import { TestBed } from '@angular/core/testing';
import { HttpClient, HTTP_INTERCEPTORS } from '@angular/common/http';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { FilterParamsInterceptor } from './filter-params.interceptor';
import { Params } from '@angular/router';

describe('Filter Params Interceptor', () => {
  const testRoute = '/test/route';

  let httpClient: HttpClient;
  let httpTestingController: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        HttpClientTestingModule,
      ],
      providers: [
        { provide: HTTP_INTERCEPTORS, useClass: FilterParamsInterceptor, multi: true }
      ]
    });

    httpClient = TestBed.inject(HttpClient);
    httpTestingController = TestBed.inject(HttpTestingController);
  });

  it('should filter empty string params', (done) => {
    httpClient.get(testRoute, { params: { a: '' } }).subscribe(() => done());

    const request = httpTestingController.expectOne(request => request.url.split('?')[0] === testRoute);
    request.flush({});

    expect(request.request.params.has('a')).toBeFalsy();
  });

  it('should filter when having multiple values', (done) => {
    httpClient.get(testRoute, { params: { a: [ '', 5 ] } }).subscribe(() => done());

    const request = httpTestingController.expectOne(request => request.url.split('?')[0] === testRoute);
    request.flush({});

    expect(request.request.params.getAll('a')).toEqual([ '5' ]);
  });

  it('should remove nullish values', (done) => {
    /*
     * when a nullish value reaches the url as a parameters, using the `map` methods on it, it will result in the
     * nullish value to be stringified.  i.e. the below will result in { a: 'null', b: 'undefined' }
     */

    httpClient.get(testRoute, { params: { a: null, b: undefined } as Params }).subscribe(() => done());

    const request = httpTestingController.expectOne(request => request.url.split('?')[0] === testRoute);
    request.flush({});

    expect(request.request.params.get('a')).not.toEqual('null');
    expect(request.request.params.get('b')).not.toEqual('undefined');
  });
});
