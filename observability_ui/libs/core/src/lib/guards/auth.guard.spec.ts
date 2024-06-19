import { TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { AuthGuard } from './auth.guard';
import { ActivatedRouteSnapshot, RouterStateSnapshot, UrlTree } from '@angular/router';
import { BehaviorSubject } from 'rxjs';
import { SessionService } from '../services/auth/session.service';

describe('Auth Guard', () => {
  let sessionService: SessionService;
  let authGuard: AuthGuard;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        MockProvider(SessionService)
      ]
    });

    sessionService = TestBed.inject(SessionService);
    authGuard = TestBed.inject(AuthGuard);

    sessionService.setLoginRedirect = jest.fn();
  });

  describe('canActivate', () => {
    describe('user logged in', () => {
      it('should return true', (done) => {
        sessionService.isLoggedIn$ = new BehaviorSubject<boolean>(true);
        authGuard.canActivate({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot).subscribe(value => {
          expect(value).toEqual(true);
          done();
        });
      });
    });

    describe('user not logged in', () => {
      beforeEach(() => {
        sessionService.isLoggedIn$ = new BehaviorSubject<boolean>(false);
      });

      it('should set login redirect to current url', (done) => {
        authGuard.canActivate({ queryParams: {} } as ActivatedRouteSnapshot, { url: '/test-redirect-url' } as RouterStateSnapshot).subscribe(() => {
          expect(sessionService.setLoginRedirect).toHaveBeenCalledWith('/test-redirect-url');
          done();
        });
      });

      it('should return a url tree to login page', (done) => {
        authGuard.canActivate({ queryParams: {} } as ActivatedRouteSnapshot, { url: '/test-redirect-url' } as RouterStateSnapshot).subscribe((url) => {
          expect((url as UrlTree)?.toString()).toEqual('/authentication');
          done();
        });
      });
    });
  });
});
