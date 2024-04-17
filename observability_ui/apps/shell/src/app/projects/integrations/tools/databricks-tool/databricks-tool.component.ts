import { Component } from '@angular/core';
import { AbstractTool } from '../abstract-tool.directive';
import { MatIconModule } from '@angular/material/icon';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatLegacyButtonModule } from '@angular/material/legacy-button';
import { ServiceKeyFormComponent } from '../../service-key-form/service-key-form.component';
import { FormControl, FormGroup, ReactiveFormsModule, ValidatorFn, Validators } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AlertComponent, CodeSnippetComponent, DkTooltipModule, TextFieldModule } from '@observability-ui/ui';
import { RouterModule } from '@angular/router';
import { CustomValidators } from '@observability-ui/core';
import { MatLegacySelectModule } from '@angular/material/legacy-select';
import { MatLegacyFormFieldModule } from '@angular/material/legacy-form-field';
import { listEnvVariableFormatter } from '@observability-ui/core';

type AuthType = 'token' | 'basic' | 'service_principal';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'databricks-tool',
  templateUrl: 'databricks-tool.component.html',
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
    DkTooltipModule,
  ],
  standalone: true,
})
export class DatabricksToolComponent extends AbstractTool {
  static override _name = 'databricks';
  static override _displayName = 'Databricks';
  static override _icon = 'databricks';
  static override _image = 'docker.io/datakitchen/observability-agent-trial';
  static override _version = 'production';

  private readonly defaultValues = {
    period: '5.0',
    timeout: '120.0',
    failedWatchPeriod: '600.0',
    failedWatchMaxTime: '604800.0',
  };

  override readonly envList = [
    { name: 'AGENT_TYPE', tpl: 'agent_type', placeholder: '' },
    { name: 'AGENT_KEY', tpl: 'agent_key', placeholder: '# assigns the identifier of the agent', required: true },
    { name: 'DK_API_URL', tpl: 'observability_base_url', placeholder: '# the URL to the Observability API', required: true },
    { name: 'DK_API_KEY', tpl: 'observability_service_account_key', placeholder: '# an API key for the Observability project', required: true },
    { name: 'HOST', tpl: 'databricks_host', placeholder: '# the URL of the Databricks instance', required: true },
    { name: 'AUTHENTICATION_TYPE', placeholder: '# method of authentication can be set to token, basic, or service_principal', required: true },
    { name: 'TOKEN', tpl: 'auth_agent_token', placeholder: '# the access token for the Databricks instance' },
    { name: 'USERNAME', tpl: 'auth_agent_username', placeholder: '# the username for basic authentication' },
    { name: 'PASSWORD', tpl: 'auth_agent_password', placeholder: '# the password for basic authentication' },
    { name: 'AZURE_TENANT_ID', tpl: 'auth_azure_tenant_id', placeholder: '# the Directory (tenant) ID of the service principal' },
    { name: 'AZURE_CLIENT_ID', tpl: 'auth_azure_client_id', placeholder: '# the Application (client) ID of the service principal' },
    { name: 'AZURE_CLIENT_SECRET', tpl: 'auth_azure_client_secret', placeholder: '# the client secret value created during the setup of the service principal' },
    {
      name: 'JOBS',
      tpl: 'databricks_jobs',
      placeholder: '# comma-separated list of job names to monitor',
      formatter: listEnvVariableFormatter,
    },
    { name: 'PERIOD', tpl: 'period', placeholder: `# the cadence at which the agent polls for information (default: ${this.defaultValues.period})`, default: this.defaultValues.period },
    { name: 'TIMEOUT', tpl: 'timeout', placeholder: `# the timeout for requests made by the agent (default: ${this.defaultValues.timeout}`, default: this.defaultValues.timeout },
    { name: 'FAILED_WATCH_PERIOD', tpl: 'databricks_failed_watch_period', placeholder: `# the cadence at which the agent polls for repaired runs (default: ${this.defaultValues.failedWatchPeriod}`, default: this.defaultValues.failedWatchPeriod },
    { name: 'FAILED_WATCH_MAX_TIME', tpl: 'databricks_failed_watch_max_time', placeholder: `# the maximum time the agent watches for repaired runs (default: ${this.defaultValues.failedWatchMaxTime}`, default: this.defaultValues.failedWatchMaxTime },
  ];

  private requiredByAuthType = {
    TOKEN: [ 'token' ],
    USERNAME: [ 'basic' ],
    PASSWORD: [ 'basic' ],
    AZURE_TENANT_ID: [ 'service_principal' ],
    AZURE_CLIENT_ID: [ 'service_principal' ],
    AZURE_CLIENT_SECRET: [ 'service_principal' ],
  };

  override envListForm = new FormGroup({
      AGENT_TYPE: new FormControl('databricks', Validators.required),
      AGENT_KEY: new FormControl('', Validators.required),
      DK_API_URL: new FormControl('', Validators.required),
      DK_API_KEY: new FormControl('', Validators.required),
      HOST: new FormControl('', Validators.required),
      AUTHENTICATION_TYPE: new FormControl<AuthType>(null, [ Validators.required, CustomValidators.oneOf([ 'token', 'service_principal', 'basic' ]) ]),
      TOKEN: new FormControl(''),
      USERNAME: new FormControl(''),
      PASSWORD: new FormControl(''),
      AZURE_TENANT_ID: new FormControl(''),
      AZURE_CLIENT_ID: new FormControl(''),
      AZURE_CLIENT_SECRET: new FormControl(''),
      JOBS: new FormControl(''),
      PERIOD: new FormControl(this.defaultValues.period, Validators.min(5)),
      TIMEOUT: new FormControl(this.defaultValues.timeout, Validators.min(15)),
      FAILED_WATCH_PERIOD: new FormControl(this.defaultValues.failedWatchPeriod, Validators.min(60)),
      FAILED_WATCH_MAX_TIME: new FormControl(this.defaultValues.failedWatchMaxTime, Validators.min(60)),
      DOCKER_TAG: new FormControl('', [ Validators.required ]),
      DEFAULT_DEPLOYMENT_MODE: new FormControl('', [ Validators.required, CustomValidators.oneOf([ 'docker', 'kubernetes' ]) ]),
    },
    Object.entries(this.requiredByAuthType).map<ValidatorFn>(([ variable, authTypes ]) => {
      return CustomValidators.requiredIf(variable, (control) => this.requiredIfCheck(variable, authTypes, control as FormGroup));
    }),
  );

  protected override hidingRules = [
    {when: 'AUTHENTICATION_TYPE', equals: ['token', 'basic'], hide: 'AZURE_TENANT_ID'},
    {when: 'AUTHENTICATION_TYPE', equals: ['token', 'basic'], hide: 'AZURE_CLIENT_ID'},
    {when: 'AUTHENTICATION_TYPE', equals: ['token', 'basic'], hide: 'AZURE_CLIENT_SECRET'},
    {when: 'AUTHENTICATION_TYPE', equals: ['service_principal', 'token'], hide: 'USERNAME'},
    {when: 'AUTHENTICATION_TYPE', equals: ['service_principal', 'token'], hide: 'PASSWORD'},
    {when: 'AUTHENTICATION_TYPE', equals: ['service_principal', 'basic'], hide: 'TOKEN'},
  ];

  protected override disableOnStart: FormControl<any>[] = [
    this.envListForm.controls['AGENT_TYPE'],
  ];

  private requiredIfCheck(variable: string, authTypes: string[], control: FormGroup): boolean {
    const required = authTypes.includes(control.controls['AUTHENTICATION_TYPE'].value);
    this.envList.find(({ name }) => name === variable).required = required;
    return required;
  }
}
