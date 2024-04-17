import { Component } from '@angular/core';
import { AbstractTool } from '../abstract-tool.directive';
import { MatIconModule } from '@angular/material/icon';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatLegacyButtonModule } from '@angular/material/legacy-button';
import { ServiceKeyFormComponent } from '../../service-key-form/service-key-form.component';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AlertComponent, CodeSnippetComponent, TextFieldModule } from '@observability-ui/ui';
import { RouterModule } from '@angular/router';
import { MatLegacySelectModule } from '@angular/material/legacy-select';
import { MatLegacyFormFieldModule } from '@angular/material/legacy-form-field';
import { CustomValidators } from '@observability-ui/core';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'airflow-tool',
  templateUrl: 'airflow-tool.component.html',
  styleUrls: [ '../tools-common.scss' ],
  imports: [
    CommonModule,
    RouterModule,
    ReactiveFormsModule,

    MatIconModule,
    MatExpansionModule,
    MatLegacyButtonModule,
    TextFieldModule,
    MatLegacySelectModule,
    MatLegacyFormFieldModule,

    AlertComponent,
    CodeSnippetComponent,
    ServiceKeyFormComponent,
  ],
  standalone: true,
})
export class AirflowToolComponent extends AbstractTool {
  static override _name = 'airflow';
  static override _displayName = 'Airflow';
  static override _icon = 'airflow';
  static override _image = 'docker.io/datakitchen/observability-agent-trial';
  static override _version = 'production';

  private readonly defaultValues = {
    period: '5.0'
  };

  override readonly envList = [
    { name: 'AGENT_TYPE', tpl: 'agent_type', placeholder: '' },
    { name: 'AGENT_KEY', tpl: 'agent_key', placeholder: '# assigns the identifier of the agent', required: true },
    { name: 'DK_API_URL', tpl: 'observability_base_url', placeholder: '# the URL to the Observability API', required: true },
    { name: 'DK_API_KEY', tpl: 'observability_service_account_key', placeholder: '# an API key for the Observability project', required: true },
    { name: 'API_URL', tpl: 'airflow_api_url', placeholder: '# the URL to the Airflow API', required: true },
    { name: 'USERNAME', tpl: 'auth_agent_username', placeholder: '# the username for an Airflow account', required: true },
    { name: 'PASSWORD', tpl: 'auth_agent_password', placeholder: '# the password for an Airflow account', required: true },
    { name: 'PERIOD', tpl: 'DK_AIRFLOW_PERIOD', placeholder: `# the cadence at which the agent polls for information (default: ${this.defaultValues.period})`, default: this.defaultValues.period },
  ];

  override envListForm = new FormGroup({
    AGENT_TYPE: new FormControl('airflow', Validators.required),
    AGENT_KEY: new FormControl('', Validators.required),
    DK_API_URL: new FormControl('', Validators.required),
    DK_API_KEY: new FormControl('', Validators.required),
    API_URL: new FormControl('', Validators.required),
    USERNAME: new FormControl('', Validators.required),
    PASSWORD: new FormControl('', Validators.required),
    PERIOD: new FormControl(this.defaultValues.period, Validators.min(5)),
    DOCKER_TAG: new FormControl('', [ Validators.required ]),
    DEFAULT_DEPLOYMENT_MODE: new FormControl('', [ Validators.required, CustomValidators.oneOf([ 'docker', 'kubernetes' ]) ]),
  });

  protected override disableOnStart: FormControl<any>[] = [
    this.envListForm.controls['AGENT_TYPE'],
  ];
}
