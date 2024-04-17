import { ComponentFixture, TestBed } from '@angular/core/testing';
import { JourneysStore } from '../journeys.store';
import { JourneySettingsComponent } from './journey-settings.component';
import { MockComponent } from 'ng-mocks';
import { ActivatedRoute } from '@angular/router';
import { of } from 'rxjs';
import { ReactiveFormsModule } from '@angular/forms';
import { MatLegacyCardModule as MatCardModule } from '@angular/material/legacy-card';
import { MatIconModule } from '@angular/material/icon';
import { JourneyInstanceRulesComponent } from '../journey-instance-rules/journey-instance-rules.component';
import { CreatedByComponent, HelpLinkComponent, MatCardEditComponent } from '@observability-ui/ui';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { MatLegacyDialog as MatDialog } from '@angular/material/legacy-dialog';

describe('JourneySettingsComponent', () => {
  const journey = {
    id: '1',
    name: 'Test Journey',
    description: 'test journey description',
    instance_rules: [ { id: '1', action: 'START', batch_pipeline: '15' } ]
  };

  let component: JourneySettingsComponent;
  let fixture: ComponentFixture<JourneySettingsComponent>;
  let journeysStore: JourneysStore;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [
        JourneySettingsComponent,
        MockComponent(JourneyInstanceRulesComponent),
        MockComponent(HelpLinkComponent),
      ],
      imports: [
        CreatedByComponent,
        ReactiveFormsModule,
        MatCardModule,
        MatIconModule,
        MatCardEditComponent,
      ],
      providers: [
        MockProvider(ActivatedRoute, class {
          parent = {
            params: of({ id: '1' })
          };
        }),
        MockProvider(JourneysStore, class {
          state$ = of({});
          selected$ = of(journey);
        }),
        MockProvider(MatDialog),
      ]
    }).compileComponents();

    journeysStore = TestBed.inject(JourneysStore);

    fixture = TestBed.createComponent(JourneySettingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should set the pipeline id to the form value', () => {
    expect(component.form.value.id).toBe('1');
  });

  it('should set the form value for all fields', () => {
    expect(journeysStore.dispatch).toBeCalledWith('findComponents', journey.id);
  });

  it('should re-fetch the journey components', () => {
    expect(component.form.value).toEqual({ ...journey, payload_instance_conditions: [] });
  });

  describe('saveInfo()', () => {
    it('should dispatch updateOne', () => {
      component.form.setValue({
        id: '1',
        name: 'my name',
        description: 'my description',
        instance_rules: [],
        payload_instance_conditions: []
      });

      component.saveInfo({ instance_rules: [ { id: '1', action: 'START', batch_pipeline: '25' } ] } as any);
      expect(journeysStore.dispatch).toHaveBeenCalledWith('updateOne', expect.objectContaining({
        id: '1',
        name: 'my name',
        description: 'my description',
      }));
    });

    it('should not keep the same instance rules', () => {
      component.form.setValue({
        id: '1',
        name: 'my name',
        description: 'my description',
        instance_rules: [],
        payload_instance_conditions: []
      });

      component.saveInfo({ instance_rules: [ { id: '1', action: 'START', batch_pipeline: '25' } ] } as any);
      expect(journeysStore.dispatch).toHaveBeenCalledWith('updateOne', {
        id: '1',
        name: 'my name',
        description: 'my description',
        instance_rules: [ { id: '1', action: 'START', batch_pipeline: '25' } ],
      });
    });
  });

  describe('cancelInfoChanges()', () => {
    it('should rollback the changes to name and description', () => {
      const journey = { name: 'original name', description: 'original description' } as any;
      component.form.patchValue({ name: 'new name', description: 'new description' });
      component.cancelInfoChanges(journey);
      expect(component.form.value).toEqual(expect.objectContaining(journey));
    });
  });

  describe('cancelConditionsChanges()', () => {
    it('should rollback the changes to instance rules', () => {
      const journey = {
        name: 'name',
        description: 'description',
        instance_rules: [ { id: '1', action: 'START', batch_pipeline: '25' } ]
      } as any;
      component.form.patchValue({ instance_rules: [] });
      component.cancelConditionsChanges(journey);
      expect(component.form.value.instance_rules).toEqual(journey.instance_rules);
    });
  });
});
