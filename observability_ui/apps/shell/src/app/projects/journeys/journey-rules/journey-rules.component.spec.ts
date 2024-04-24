import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatLegacyCardModule as MatCardModule } from '@angular/material/legacy-card';
import { MatLegacySelectModule as MatSelectModule } from '@angular/material/legacy-select';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { ActivatedRouteMock } from '@datakitchen/ngx-toolkit';
import { ActivatedRoute } from '@angular/router';
import { of } from 'rxjs';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { MatIconModule } from '@angular/material/icon';
import { MatLegacyMenuModule as MatMenuModule } from '@angular/material/legacy-menu';
import { DynamicComponentModule } from '@observability-ui/ui';
import { MockComponent } from 'ng-mocks';
import { MatProgressSpinner } from '@angular/material/progress-spinner';
import { JourneyRulesComponent } from './journey-rules.component';
import { RuleStore } from '../../../components/rules-actions/rule.store';
import { JourneysStore } from '../journeys.store';
import { MatLegacyDialog as MatDialog } from '@angular/material/legacy-dialog';
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import { ComponentType } from '@observability-ui/core';

describe('journey-rules', () => {
  const components = [ {id: '1', name: 'Pipeline A', type: ComponentType.BatchPipeline} ];

  let component: JourneyRulesComponent;
  let fixture: ComponentFixture<JourneyRulesComponent>;
  let dialog: MatDialog;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        MatCardModule,
        MatSelectModule,
        NoopAnimationsModule,
        MatIconModule,
        MatMenuModule,
        DynamicComponentModule,
      ],
      declarations: [
        JourneyRulesComponent,
        MockComponent(MatProgressSpinner),
      ],
      providers: [
        MockProvider(RuleStore, class {
          getLoadingFor = () => of(false);
        }),
        MockProvider(JourneysStore, class {
          components$ = of(components);
        }),
        MockProvider(MatDialog),
        {
          provide: ActivatedRoute,
          useValue: ActivatedRouteMock({}, {}, ActivatedRouteMock({id: 'journeyId'})),
        }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(JourneyRulesComponent);
    component = fixture.componentInstance;

    dialog = TestBed.inject(MatDialog);

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should open rule create dialog', () => {
    component.openRuleDialog();
    expect(dialog.open).toHaveBeenCalled();
  });

  it('should populate the list of components', () => {
    new TestScheduler().run(({flush}) => {
      flush();
      expect(component.components.length).toBe(1);
    });
  });
});
