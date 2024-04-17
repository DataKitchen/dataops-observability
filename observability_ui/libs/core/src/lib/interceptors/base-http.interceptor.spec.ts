import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { HTTP_INTERCEPTORS, HttpClient } from '@angular/common/http';
import { BaseHttpInterceptor } from '../interceptors/base-http.interceptor';
import { Mocked, MockProvider } from '@datakitchen/ngx-toolkit';
import { MatLegacySnackBar as MatSnackBar } from '@angular/material/legacy-snack-bar';
import { SessionService } from '../services';

describe('Base HTTP Interceptor', () => {
  const testRoute = '/test/route';
  const excludedRoute = '/v1/auth/basic';

  let snackBar: Mocked<MatSnackBar>;
  let httpClient: HttpClient;
  let httpTestingController: HttpTestingController;
  let sessionService: SessionService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        HttpClientTestingModule,
      ],
      providers: [
        MockProvider(SessionService, class {
          removeToken = jest.fn();
        }),
        MockProvider(MatSnackBar, class {}),
        {provide: HTTP_INTERCEPTORS, useClass: BaseHttpInterceptor, multi: true}
      ]
    });

    snackBar = TestBed.inject(MatSnackBar) as Mocked<MatSnackBar>;

    httpClient = TestBed.inject(HttpClient);
    httpTestingController = TestBed.inject(HttpTestingController);
    sessionService = TestBed.inject(SessionService);
  });

  it('should set token if token is not null', () => {
    sessionService.getToken = jest.fn().mockImplementation(() => {
      return 'test_token';
    });

    httpClient.get(testRoute).subscribe();

    const request = httpTestingController.expectOne(testRoute);
    request.flush({ code: 'success' }, { status: 200, statusText: 'Ok' });

    expect(request.request.headers.get('Authorization')).toEqual('Bearer test_token');

    httpTestingController.verify();
  });

  it('should not set token if URL is excluded', () => {
    sessionService.getToken = jest.fn().mockImplementation(() => {
      return 'test_token';
    });

    httpClient.get(excludedRoute).subscribe();

    const request = httpTestingController.expectOne(excludedRoute);
    request.flush({ code: 'success' }, { status: 200, statusText: 'Ok' });

    expect(request.request.headers.get('Authorization')).toBeNull();

    httpTestingController.verify();
  });

  it('should unset token and redirect to login on 401 response', (done) => {
    httpClient.get(testRoute).subscribe(
      () => {
        fail();
      },
      () => {
        expect(sessionService.removeToken).toHaveBeenCalled();
        expect(snackBar.open).toHaveBeenCalled();
        done();
      }
    );

    const request = httpTestingController.expectOne(testRoute);
    request.flush({ code: 'token_expired' }, { status: 401, statusText: 'Unauthorized' });

    httpTestingController.verify();
  });

  it('should redirect on 403 response', (done) => {
    httpClient.get(testRoute).subscribe(
      () => {
        fail();
      },
      () => {
        expect(snackBar.open).toHaveBeenCalled();
        done();
      }
    );

    const request = httpTestingController.expectOne(testRoute);
    request.error(new ErrorEvent('Forbidden'), { status: 403 });

    httpTestingController.verify();
  });
});
