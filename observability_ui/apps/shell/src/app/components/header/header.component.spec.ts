import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HeaderComponent } from './header.component';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { SessionService, ConfigService } from '@observability-ui/core';
import { MatLegacyMenuModule as MatMenuModule } from '@angular/material/legacy-menu';
import { MatIconModule } from '@angular/material/icon';
import { RouterTestingModule } from '@angular/router/testing';
import { of } from 'rxjs';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

describe('HeaderComponent', () => {

  let component: HeaderComponent;
  let fixture: ComponentFixture<HeaderComponent>;

  let sessionService: SessionService;

  const mockUser = { name: 'test-user', id: '1' };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [
        HeaderComponent,
      ],
      imports: [
        HttpClientTestingModule,
        MatMenuModule,
        MatIconModule,
        RouterTestingModule,
        NoopAnimationsModule,
      ],
      providers: [
        MockProvider(SessionService, class {
          isLoggedIn$ = of(true);
          user$ = of(mockUser);
          setPrototypeAnalytics = jest.fn();
        }),
        MockProvider(ConfigService, class {
          get = () => 'base';
        }),
      ]
    }).compileComponents();

    sessionService = TestBed.inject(SessionService);

    sessionService.endSession = jest.fn();

    fixture = TestBed.createComponent(HeaderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

  });


  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('endSession', () => {
    beforeEach(() => {
      component.logout();
    });

    it('should call auth service logout method', () => {
      expect(sessionService.endSession).toHaveBeenCalled();
    });

  });

  describe('openSmallHelpWindow', () => {
    it('should call window open with url and features', () => {
      window.open = jest.fn();
      component.openSmallHelpWindow('test');
      expect(window.open).toHaveBeenCalledWith('https://docs.datakitchen.io/test', '_blank', "toolbar=0,scrollbars=1,location=0,statusbar=0,menubar=0,resizable=1,width=800,height=600,top=700,left=700");
    });
  });
});
