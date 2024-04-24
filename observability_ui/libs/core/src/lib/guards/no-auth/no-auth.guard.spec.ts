import { TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { NoAuthGuard } from './no-auth.guard';
import { BehaviorSubject } from 'rxjs';
import { SessionService } from '../../services/auth/session.service';

describe('No Auth Guard', () => {
  let authService: SessionService;
  let authGuard: NoAuthGuard;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        MockProvider(SessionService)
      ]
    });

    authService = TestBed.inject(SessionService);
    authGuard = TestBed.inject(NoAuthGuard);
  });

  describe('canActivate', () => {
    it('should return true if user not logged in', (done) => {
      authService.isLoggedIn$ = new BehaviorSubject<boolean>(false);
      authGuard.canActivate().subscribe(value => {
        expect(value).toEqual(true);
        done();
      });
    });

    it('should return false if user logged in', (done) => {
      authService.isLoggedIn$ = new BehaviorSubject<boolean>(true);
      authGuard.canActivate().subscribe(value => {
        expect(value).toEqual(false);
        done();
      });
    });
  });
});
