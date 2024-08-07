import { ProjectAlertsComponent } from "./project-alerts.component";
import { ComponentFixture, TestBed } from "@angular/core/testing";
import { ProjectAlertSettingsStore } from "./project-alerts.store";
import { ProjectService, ProjectStore, RULE_ACTIONS } from "@observability-ui/core";
import { Mocked, MockProvider } from "@datakitchen/ngx-toolkit";
import { MatLegacySnackBar } from "@angular/material/legacy-snack-bar";
import { ExampleActionComponent } from "../rules-actions/implementations/actions/example/example-action.component";
import { of } from "rxjs";
import { DynamicComponentModule } from "@observability-ui/ui";
import { NoopAnimationsModule } from "@angular/platform-browser/animations";


describe('ProjectAlertsComponent', () => {
  let component: ProjectAlertsComponent;
  let store: ProjectAlertSettingsStore;
  let fixture: ComponentFixture<ProjectAlertsComponent>;

  let initialSettings = {
      agent_check_interval: 65,
      actions: [
        {action_impl: "EXAMPLE_ACTION", action_args: "args1"},
        {action_impl: "EXAMPLE_ACTION", action_args: "args2"},
      ],
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        DynamicComponentModule,
        NoopAnimationsModule,
      ],
      providers: [
        ProjectAlertsComponent,
        MockProvider(ProjectAlertSettingsStore, class {
          alertSettings$ = of(initialSettings);
          getLoadingFor = () => of(false);
          loading$ = of({});
          dispatch = jest.fn();
        }),
        MockProvider(ProjectStore, class {
          current$ = of({id: "project_id"});
        }),
        MockProvider(MatLegacySnackBar),
        MockProvider(ProjectService),
        {
          provide: RULE_ACTIONS,
          useValue: [ ExampleActionComponent ]
        },
      ]
    }).compileComponents();

    store = TestBed.inject(ProjectAlertSettingsStore) as Mocked<ProjectAlertSettingsStore>;
    fixture = TestBed.createComponent(ProjectAlertsComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load the current settings', () => {
    expect(component.actionDisplayerDirective.length).toBe(2);
    expect(component.form.value).toStrictEqual({ agent_check_interval: 65 });
  });

  describe("saveSettings", () => {
    it('should save', () => {
      component.saveSettings();
      expect(store.dispatch).toHaveBeenLastCalledWith(
          "update",
          "project_id",
          {
            "actions": [
              {"action_args": "args1", "action_impl": "EXAMPLE_ACTION"},
              {"action_args": "args2", "action_impl": "EXAMPLE_ACTION"}
            ],
            "agent_check_interval": 65
          }
      );
    });
  });

  describe("addAction", () => {
    it('should add', () => {
      component.addAction(ExampleActionComponent);
      fixture.detectChanges();
      expect(component.actionDisplayerDirective.length).toBe(3);
    });
  });

  describe("removeAction", () => {
    it('should remove one', () => {
      component.removeAction(1);
      fixture.detectChanges();
      expect(component.actionDisplayerDirective.length).toBe(1);
    });
    it('should not remove non existing', () => {
      component.removeAction(3);
      fixture.detectChanges();
      expect(component.actionDisplayerDirective.length).toBe(2);
    });
  });

  describe("isInputValid", () => {
    it('should validate', () => {
      expect(component.isInputValid()).toBeTruthy();
    });
    it('should not validate', () => {
      component.actionDisplayerDirective.get(0)?.ref.instance.form.setValue(undefined);
      expect(component.isInputValid()).toBeFalsy();
    });
    it('should not validate', () => {
      component.form.setValue({ agent_check_interval: 45 });
      expect(component.isInputValid()).toBeFalsy();
    });
  });
});
