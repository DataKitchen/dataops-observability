import { TestBed, fakeAsync, tick } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { cookieKeys, cookiePath, localStorageKeys } from './auth.model';
import { CookieService } from 'ngx-cookie-service';
import { JWT_OPTIONS, JwtHelperService } from '@auth0/angular-jwt';
import { SessionService } from './session.service';
import { ConfigService } from '../../config/config.service';
import { MockProvider } from 'ng-mocks';
import { RouterTestingModule } from '@angular/router/testing';
import { Router } from '@angular/router';
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import spyOn = jest.spyOn;
import { of } from 'rxjs';

describe('Session Service', () => {
  let sessionService: SessionService;
  let cookieService: CookieService;
  let router: Router;
  let testScheduler: TestScheduler;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        HttpClientTestingModule,
        RouterTestingModule,
      ],
      providers: [
        SessionService,
        MockProvider(CookieService, {
          get: () => 'valid-token'
        }),
        MockProvider(JwtHelperService, {
          isTokenExpired: () => false,
        } as any),
        {
          provide: ConfigService,
          useClass: class {
            get = () => 'base';
          }
        },
        { provide: JWT_OPTIONS, useValue: JWT_OPTIONS }
      ]
    });

    sessionService = TestBed.inject(SessionService);
    cookieService = TestBed.inject(CookieService);
    router = TestBed.inject(Router);
    spyOn(router, 'navigate').mockImplementation(() => Promise.resolve(true));

    cookieService.set = jest.fn();
    cookieService.delete = jest.fn();
    testScheduler = new TestScheduler();
  });

  it('should create', () => {
    expect(sessionService).toBeTruthy();
  });

  it('should set auth state', () => {
    testScheduler.expectObservable(sessionService.isLoggedIn$).toEqual(of(true));
  });

  describe('setLoginRedirect()', () => {
    it('should set redirect url in localStorage', () => {
      const url = 'test_url';
      sessionService.setLoginRedirect(url);
      expect(localStorage.getItem(localStorageKeys.loginRedirect)).toEqual(url);
    });
  });

  describe('getLoginRedirect()', () => {
    it('should get redirect url from localStorage', () => {
      const url = 'test_url';
      localStorage.setItem(localStorageKeys.loginRedirect, url);
      expect(sessionService.getLoginRedirect()).toEqual(url);
    });
  });

  describe('setToken()', () => {
    it('should set the token into the cookies', () => {
      const token = 'my-test-token';
      sessionService.setToken(token);
      expect(cookieService.set).toBeCalledWith(cookieKeys.token, token, { path: cookiePath });
    });
  });

  describe('endSession()', () => {
    it('should set isLoggedIn$ observable with false value', () => {
      sessionService.endSession();
      testScheduler.expectObservable(sessionService.isLoggedIn$).toEqual(of(false));
    });

    it('should navigate to login', fakeAsync(() => {
      sessionService.endSession();
      tick();
      expect(router.navigate).toHaveBeenCalledWith(['/authentication/logout']);
    }));
  });
});
