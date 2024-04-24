import { ComponentFixture, TestBed } from '@angular/core/testing';
import { IntegrationsComponent } from './integrations.component';
import { Mocked, MockProvider } from '@datakitchen/ngx-toolkit';
import { Agent, AgentStore, ProjectStore } from '@observability-ui/core';
import { rxjsScheduler } from '@datakitchen/ngx-toolkit';
import { of } from 'rxjs';
import { TranslatePipeMock } from '@observability-ui/translate';
import { MockComponents, MockModule, MockPipes } from 'ng-mocks';
import { BreadcrumbComponent, TextFieldComponent } from '@observability-ui/ui';
import { MatIcon, MatIconModule } from '@angular/material/icon';
import { RouterTestingModule } from '@angular/router/testing';
import { MatLegacyPaginator as MatPaginator } from '@angular/material/legacy-paginator';
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import { ToolSelectorComponent } from './tool-selector/tool-selector.component';
import { ReactiveFormsModule } from '@angular/forms';
import { MatCard } from '@angular/material/card';
import { GetToolClassPipe } from './tool-selector/get-tool-class.pipe';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

describe('integrations', () => {

  let component: IntegrationsComponent;
  let fixture: ComponentFixture<IntegrationsComponent>;
  let store: Mocked<AgentStore>;

  let testScheduler: TestScheduler;

  beforeEach(async () => {

    testScheduler = new TestScheduler();

    await TestBed.configureTestingModule({
      imports: [
        RouterTestingModule,
        ReactiveFormsModule,
        MatIconModule,
        MockModule(MatProgressSpinnerModule),
      ],
      declarations: [
        IntegrationsComponent,
        TranslatePipeMock,
        MockComponents(
          BreadcrumbComponent,
          MatIcon,
          MatPaginator,
          TextFieldComponent,
          ToolSelectorComponent,
          MatCard,
        ),
        MockPipes(
          GetToolClassPipe,
        )
      ],
      providers: [
        {
          provide: rxjsScheduler,
          useValue: testScheduler,
        },
        MockProvider(ProjectStore, class {
          selected$ = of({id: 'projectId'});
        }),
        MockProvider(AgentStore, class {
          getLoadingFor = () => of(false);
          list$ = of([{key: '__key__', tool: '__tool__'}]);
        }),
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(IntegrationsComponent);
    store = TestBed.inject(AgentStore) as Mocked<AgentStore>;
    component = fixture.componentInstance;

    fixture.detectChanges();
    testScheduler.flush();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load agents', () => {
    expect(store.dispatch).toHaveBeenCalledWith('getPage', expect.anything());
  });

  describe('#calculateLateness', () => {

    it('should add difference between now and the latest heartbeat in seconds', () => {
      const heartBeat = new Date();
      heartBeat.setMilliseconds(heartBeat.getMilliseconds() - 32_750);

      const agent = {
        latest_heartbeat: heartBeat,
      };

      expect(component['calculateLateness'](agent as unknown as Agent).lateness).toEqual(32);
    });
  });

});
