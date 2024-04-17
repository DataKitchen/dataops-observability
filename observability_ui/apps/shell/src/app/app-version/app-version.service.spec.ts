import { TestBed } from '@angular/core/testing';
import { AppVersionService } from './app-version.service';
import { MatBottomSheetModule } from '@angular/material/bottom-sheet';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { SwUpdate, VersionEvent } from '@angular/service-worker';
import { BehaviorSubject, of } from 'rxjs';
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import { rxjsScheduler } from '@datakitchen/ngx-toolkit';

describe('AppVersionService', () => {
  let service: AppVersionService;

  const versionUpdates = new BehaviorSubject<VersionEvent | null>(null);

  let http: HttpTestingController;
  let scheduler: TestScheduler;

  beforeEach(() => {

    scheduler = new TestScheduler();

    jest.spyOn(console, 'log').mockImplementation();

    TestBed.configureTestingModule({
      imports: [
        HttpClientTestingModule,
        MatBottomSheetModule,
      ],
      providers: [
        {
          provide: SwUpdate,
          useClass: class {
            versionUpdates = versionUpdates;
            isEnabled = true;
            checkForUpdate = jest.fn().mockReturnValue(of({}));
          }
        },
        {
          provide: rxjsScheduler,
          useValue: scheduler,
        }
      ]
    });

    service = TestBed.inject(AppVersionService);
    http = TestBed.inject(HttpTestingController);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should get app version', () => {
    http.expectOne('/ngsw.json').flush({appData: {shell: 1}});
    scheduler.expect$(service.currentVersion$).toContain({ shell: 1 });
  });
});
