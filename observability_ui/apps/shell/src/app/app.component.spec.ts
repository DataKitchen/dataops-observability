import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AppComponent } from './app.component';
import { RouterTestingModule } from '@angular/router/testing';
import { MatBottomSheetModule } from '@angular/material/bottom-sheet';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { AppVersionService } from './app-version/app-version.service';
import { BehaviorSubject, of, ReplaySubject } from 'rxjs';
import { MockComponent } from 'ng-mocks';
import { HeaderComponent } from './components/header/header.component';
import { SessionService, EntitiesResolver, ProjectStore } from '@observability-ui/core';
import { MatSidenavModule } from '@angular/material/sidenav';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { MatLegacyListModule as MatListModule } from '@angular/material/legacy-list';
import { SidenavMenuComponent } from './components/sidenav-menu/sidenav-menu.component';
import { MockProvider } from '@datakitchen/ngx-toolkit';

describe('AppComponent', () => {

  let component: AppComponent;
  let fixture: ComponentFixture<AppComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        RouterTestingModule,
        MatBottomSheetModule,
        MatToolbarModule,
        MatIconModule,
        MatSidenavModule,
        MatListModule,
        NoopAnimationsModule,
      ],
      declarations: [
        AppComponent,
        MockComponent(HeaderComponent),
        MockComponent(SidenavMenuComponent),
      ],
      providers: [
        MockProvider(AppVersionService, class {
          currentVersion$ = of({}) as ReplaySubject<any>;
        }),
        MockProvider(SessionService, class {
          isLoggedIn$ = of(true) as BehaviorSubject<boolean>;
          user$ = of({primary_company: {id: 'id'}});
        }),
        MockProvider(EntitiesResolver, class {
          organization$ = of({id: 'org'});
        }),
        MockProvider(ProjectStore, class {
          current$ = of({});
        }),
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(AppComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create the app', () => {
    expect(component).toBeTruthy();
  });
});
