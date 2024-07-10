import { Component, effect, Inject, QueryList, ViewChildren } from '@angular/core';
import { ActionType, EntitiesResolver, ProjectAlertSettings, ProjectAlertSettingsAction, ProjectStore } from '@observability-ui/core';
import { NgForOf, NgIf } from '@angular/common';
import { DynamicComponentModule, DynamicComponentOutletDirective, MatCardEditComponent, TextFieldModule } from '@observability-ui/ui';
import { WebhookActionComponent } from "../rules-actions/implementations/actions/webhook/webhook-action.component";
import { SendEmailActionComponent } from "../rules-actions/implementations/actions/send-email/send-email-action.component";
import { toSignal } from "@angular/core/rxjs-interop";
import { ProjectAlertSettingsStore } from "./project-alerts.store";
import { TypedFormControl } from "@datakitchen/ngx-toolkit";
import { FormGroup, FormsModule, ReactiveFormsModule} from "@angular/forms";
import { MatLegacyInputModule as MatInputModule } from "@angular/material/legacy-input";
import { RulesActionsModule } from "../rules-actions/rules-actions.module";
import { MatIconModule } from "@angular/material/icon";
import { MatLegacyMenuModule } from "@angular/material/legacy-menu";
import { RULE_ACTIONS } from "../rules-actions/actions.model";
import { AbstractAction } from "../rules-actions/abstract-action.directive";
import { MatLegacyButtonModule } from "@angular/material/legacy-button";
import { MatExpansionModule } from "@angular/material/expansion";


interface ActionComponentInstance {
  component: typeof AbstractAction;
  data: any;
  editing: boolean;
}

@Component({
  selector: 'shell-project-alerts',
  templateUrl: 'project-alerts.component.html',
  styleUrls: [ 'project-alerts.component.scss' ],
  standalone: true,
  imports: [
    NgIf,
    WebhookActionComponent,
    SendEmailActionComponent,
    MatCardEditComponent,
    FormsModule,
    ReactiveFormsModule,
    TextFieldModule,
    MatInputModule,
    RulesActionsModule,
    MatIconModule,
    NgForOf,
    MatLegacyMenuModule,
    MatLegacyButtonModule,
    MatExpansionModule,
    DynamicComponentModule,
  ]
})
export class ProjectAlertsComponent {

  alertSettings = toSignal(this.store.alertSettings$);

  currentProject = toSignal(this.projectStore.current$);

  constructor(
    private entities: EntitiesResolver,
    private store: ProjectAlertSettingsStore,
    private projectStore: ProjectStore,
    @Inject(RULE_ACTIONS) public actionComponents: typeof AbstractAction[],
  ) {
    effect(() => {
      const projectId = this.currentProject()?.id;
      this.store.dispatch('get', projectId);
    });
  }

  ngOnInit(): void {
    this.store.alertSettings$.subscribe((settings) => {
      this.resetUiState(settings);
    });
  }

  @ViewChildren('actions', { read: DynamicComponentOutletDirective })
  actionDisplayerDirective!: QueryList<DynamicComponentOutletDirective<AbstractAction>>;

  alertActions: ActionComponentInstance[] = [];

  form = new FormGroup({
    agent_check_interval: new TypedFormControl<number>()
  });

  saving = toSignal(this.store.getLoadingFor('update'));

  resetUiState(settings: ProjectAlertSettings) {
    this.form.patchValue(settings);
    this.alertActions= settings.actions.map((entry: ProjectAlertSettingsAction) => {
        return {
          component: this.actionComponents.find((component) => component._type === entry.action_impl),
          data: entry.action_args,
          editing: false,
        };
    });
  }

  saveAction() {
    let data = {
      actions: this.actionDisplayerDirective.map((actionComponent) => {
        let json = actionComponent.ref.instance.toJSON();
        return {action_impl: json.action, action_args: json.action_args};
      }),
      ...this.form.value,
    };
    this.store.dispatch("update", this.currentProject()?.id, <ProjectAlertSettings>data);
  }

  cancelAction() {
    this.resetUiState(this.alertSettings());
  }

  addActionAction(component: typeof AbstractAction) {
    let data = {};
    if (component._type == ActionType.SendEmail) {
      data = {template: "agent_status_change", recipients: []};
    }
    this.alertActions.push(
      {component: component, data: data, editing: true}
    );
  }

  removeActionAction(idx: number) {
    this.alertActions.splice(idx, 1);
  }
}
