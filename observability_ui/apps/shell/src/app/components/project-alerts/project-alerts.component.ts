import { Component, Inject, QueryList, ViewChildren } from '@angular/core';
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
import { filter, tap } from "rxjs";
import { MatLegacySnackBar as MatSnackBar } from "@angular/material/legacy-snack-bar";
import { DefaultErrorHandlerComponent } from "../default-error-handler/default-error-handler.component";


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

  @ViewChildren('actions', { read: DynamicComponentOutletDirective })
  actionDisplayerDirective!: QueryList<DynamicComponentOutletDirective<AbstractAction>>;

  alertActions: ActionComponentInstance[] = [];

  form = new FormGroup({
    agent_check_interval: new TypedFormControl<number>()
  });

  saving = toSignal(this.store.getLoadingFor('update'));

  errorMsg: string = "";

  constructor(
    private snackbar: MatSnackBar,
    private entities: EntitiesResolver,
    private store: ProjectAlertSettingsStore,
    private projectStore: ProjectStore,
    @Inject(RULE_ACTIONS) public actionComponents: typeof AbstractAction[],
  ) {
  }

  ngOnInit(): void {

    this.store.alertSettings$.subscribe((settings) => {
      this.resetUiState(settings);
    });

    this.store.dispatch('get', this.currentProject()?.id);

  }

  loading$ = this.store.loading$.pipe(
    filter(({ code }) => code === "update" ),
    tap(({ error, status }) => {
      console.log(error);
      console.log(status);
      if (error) {
        if (error.status === 400) {
          this.errorMsg = "Error configuring actions. Please contact a system administrator";
        } else {
          this.snackbar.openFromComponent(DefaultErrorHandlerComponent, {
            data: error,
            duration: 2000,
          });
        }
      }
    }),
  ).subscribe();

  resetUiState(settings: ProjectAlertSettings) {
    this.form.patchValue(settings);
    this.alertActions= settings.actions.map((entry: ProjectAlertSettingsAction) => {
        return {
          component: this.actionComponents.find((component) => component._type === entry.action_impl),
          data: entry.action_args,
          editing: false,
        };
    });
    this.errorMsg = "";
  }

  saveSettings() {
    let data: ProjectAlertSettings = {
      actions: this.actionDisplayerDirective.map((actionComponent) => {
        let json = actionComponent.ref.instance.toJSON();
        return {action_impl: json.action, action_args: json.action_args};
      }),
      agent_check_interval: this.form.value.agent_check_interval,

    };
    this.store.dispatch("update", this.currentProject()?.id, data);
  }

  cancelSettingsChanges() {
    this.resetUiState(this.alertSettings());
  }

  addAction(component: typeof AbstractAction) {
    let data = {};
    if (component._type == ActionType.SendEmail) {
      data = {template: "agent_status_change", recipients: []};
    }
    this.alertActions.push(
      {component: component, data: data, editing: true}
    );
  }

  removeAction(idx: number) {
    this.alertActions.splice(idx, 1);
  }
}
