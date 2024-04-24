import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute } from '@angular/router';
import { of } from 'rxjs';
import { MockComponents, MockDirective, MockModule, MockPipe, MockProvider } from 'ng-mocks';
import { RouterTestingModule } from '@angular/router/testing';
import { TranslationModule } from '@observability-ui/translate';
import { DetailsHeaderComponent, DurationPipe } from '@observability-ui/ui';
import { MatLegacyTabLink as MatTabLink, MatLegacyTabNav as MatTabNav, MatLegacyTabNavPanel as MatTabNavPanel } from '@angular/material/legacy-tabs';
import { InstanceDetailsComponent } from './instance-details.component';
import { InstancesStore } from '../../../stores/instances/instances.store';
import { InstanceAlertsComponent } from '../instance-alerts/instance-alerts.component';
import { MatLegacyDialog } from '@angular/material/legacy-dialog';
import { ProjectStore } from '@observability-ui/core';

describe('InstanceDetailsComponent', () => {
  let component: InstanceDetailsComponent;
  let fixture: ComponentFixture<InstanceDetailsComponent>;

  let instancesStore: InstancesStore;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [
        InstanceDetailsComponent,
        MockComponents(DetailsHeaderComponent, MatTabNavPanel, MatTabNav, InstanceAlertsComponent),
        MockDirective(MatTabLink),
        MockPipe(DurationPipe),
      ],
      imports: [
        RouterTestingModule,
        MockModule(TranslationModule),
        InstanceAlertsComponent
      ],
      providers: [
        MockProvider(MatLegacyDialog),
        MockProvider(ProjectStore),
        MockProvider(ActivatedRoute, {
          params: of({ id: '1' })
        }),
        MockProvider(InstancesStore, {
          selected$: of({journey: {id: '1', name: 'Journey A'}}),
          dispatch: jest.fn(),
        } as any),
      ]
    }).compileComponents();

    instancesStore = TestBed.inject(InstancesStore);

    fixture = TestBed.createComponent(InstanceDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should get the instance with the store', () => {
    expect(instancesStore.dispatch).toHaveBeenCalledWith('getOne', '1');
  });
});
