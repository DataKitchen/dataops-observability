import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LoginComponent } from './login.component';
import { BasicAuthService } from '../services/auth.service';
import { Subject, of, throwError } from 'rxjs';
import { RouterTestingModule } from '@angular/router/testing';
import { MockProvider, Mocked } from '@datakitchen/ngx-toolkit';

describe('LoginComponent', () => {
  let component: LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;

  let authService: Mocked<BasicAuthService>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        NoopAnimationsModule,
        LoginComponent,
        RouterTestingModule,
      ],
      providers: [
        MockProvider(BasicAuthService, class {
          login = jest.fn();
        }),
      ],
    })
    .compileComponents();

    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    authService = TestBed.inject(BasicAuthService) as Mocked<BasicAuthService>;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('login()', () => {
    const username = 'testuser@domain.com';
    const password = 'testpassword';

    beforeEach(() => {
      console.error = jest.fn();
      component.form.patchValue({ username, password });
    });

    it('should set loginError to undefined', () => {
      const subject = new Subject();
      authService.login.mockReturnValue(subject.asObservable());

      component.loginError = '...';
      component.login();
      expect(component.loginError).toBeUndefined();
    });

    it('should call the auth service with the credentials', () => {
      authService.login.mockReturnValue(of({}));

      component.login();
      expect(authService.login).toBeCalledWith({ username, password });
    });

    it('should set loginError in case of failure', () => {
      const error = { message: 'something happened' };
      authService.login.mockReturnValue(throwError(() => error));

      component.login();
      expect(component.loginError).toEqual(error.message);
    });

    it('should log the original error in case of failure', () => {
      const originalError = { message: 'something happened' };
      authService.login.mockReturnValue(throwError(() => originalError));

      component.login();
      expect(console.error).toBeCalledWith(originalError);
    });
  });
});
