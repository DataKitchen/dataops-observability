import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AppVersionComponent } from './app-version.component';
import { MatBottomSheetModule } from '@angular/material/bottom-sheet';
import { AppVersionService } from './app-version.service';
import { of } from 'rxjs';

describe('AppVersionComponent', () => {
  let component: AppVersionComponent;
  let fixture: ComponentFixture<AppVersionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        MatBottomSheetModule
      ],
      declarations: [
        AppVersionComponent,
      ],
      providers: [
        {
            provide: AppVersionService,
            useClass: class {
              currentVersion$ = of({});
              nextVersion$ = of({});
            },
        },
      ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AppVersionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
