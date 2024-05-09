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
import { MatLegacyFormFieldModule } from '@angular/material/legacy-form-field';
import { MatLegacySelectModule } from '@angular/material/legacy-select';
import { listEnvVariableFormatter } from '@observability-ui/core';

type AuthType = 'service_principal' | 'oauth2';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'power-bi-tool',
  templateUrl: 'power-bi-tool.component.html',
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
    DkTooltipModule,
    ServiceKeyFormComponent,
  ],
  standalone: true,
})
export class PowerBIToolComponent extends AbstractTool {
  static override _name = 'power_bi';
  static override _displayName = 'Microsoft Power BI';
  static override _icon = 'power_bi';
  static override _image = 'docker.io/datakitchen/dataops-observability-agents';
  static override _version = 'production';

  private readonly defaultValues = {
    period: '5.0',
    datasetPeriod: '15.0',
  };

  override readonly envList = [
    { name: 'AGENT_TYPE', tpl: 'agent_type', placeholder: '' },
    { name: 'AGENT_KEY', tpl: 'agent_key', placeholder: '# assigns the identifier of the agent', required: true },
    { name: 'DK_API_URL', tpl: 'observability_base_url', placeholder: '# the base API URL for Observability', required: true },
    { name: 'DK_API_KEY', tpl: 'observability_service_account_key', placeholder: '# an API key for the Observability project', required: true },
    { name: 'AUTHENTICATION_TYPE', placeholder: '# method of authentication can be set to service_principal or oauth2', required: true },
    { name: 'TENANT_ID', tpl: 'auth_azure_tenant_id', placeholder: '# the Directory (tenant) ID of the service principal', required: true },
    { name: 'CLIENT_ID', tpl: 'auth_azure_client_id', placeholder: '# the Application (client) ID of the service principal', required: true },
    { name: 'CLIENT_SECRET', tpl: 'auth_azure_client_secret', placeholder: '# the client secret value created during the setup of the service principal' },
    { name: 'USERNAME', tpl: 'auth_azure_username', placeholder: '# the username for OAuth2 authentication' },
    { name: 'PASSWORD', tpl: 'auth_azure_password', placeholder: '# the password for OAuth2 authentication' },
    {
      name: 'GROUPS',
      tpl: 'powerbi_groups',
      placeholder: '# comma-separated list of group names to monitor',
      formatter: listEnvVariableFormatter,
    },
    { name: 'PERIOD', tpl: 'DK_POWERBI_PERIOD', placeholder: `# the cadence at which the agent polls for dataset refresh activity (default: ${this.defaultValues.period})`, default: this.defaultValues.period },
    { name: 'DATASETS_FETCHING_PERIOD', tpl: 'powerbi_datasets_fetching_period', placeholder: `# the cadence at which the agent polls for new datasets (default: ${this.defaultValues.datasetPeriod}`, default: this.defaultValues.datasetPeriod },
  ];

  private requiredByAuthType = {
    CLIENT_SECRET: [ 'service_principal' ],
    USERNAME: [ 'oauth2' ],
    PASSWORD: [ 'oauth2' ],
  };

  override envListForm = new FormGroup({
      AGENT_TYPE: new FormControl('power_bi', Validators.required),
      AGENT_KEY: new FormControl('', Validators.required),
      DK_API_URL: new FormControl('', Validators.required),
      DK_API_KEY: new FormControl('', Validators.required),
      AUTHENTICATION_TYPE: new FormControl<AuthType>(null, [ Validators.required, CustomValidators.oneOf([ 'service_principal', 'oauth2' ]) ]),
      TENANT_ID: new FormControl('', Validators.required),
      CLIENT_ID: new FormControl('', Validators.required),
      CLIENT_SECRET: new FormControl(''),
      USERNAME: new FormControl(''),
      PASSWORD: new FormControl(''),
      GROUPS: new FormControl(''),
      PERIOD: new FormControl(this.defaultValues.period, Validators.min(5)),
      DATASETS_FETCHING_PERIOD: new FormControl(this.defaultValues.datasetPeriod, Validators.min(15)),
      DOCKER_TAG: new FormControl('', [ Validators.required ]),
      DEFAULT_DEPLOYMENT_MODE: new FormControl('', [ Validators.required, CustomValidators.oneOf([ 'docker', 'kubernetes' ]) ]),
    },
    Object.entries(this.requiredByAuthType).map<ValidatorFn>(([ variable, authTypes ]) => {
      return CustomValidators.requiredIf(variable, (control) => this.requiredIfCheck(variable, authTypes, control as FormGroup));
    }),
  );

  protected override hidingRules = [
    {when: 'AUTHENTICATION_TYPE', equals: 'oauth2', hide: 'CLIENT_SECRET'},
    {when: 'AUTHENTICATION_TYPE', equals: 'service_principal', hide: 'USERNAME'},
    {when: 'AUTHENTICATION_TYPE', equals: 'service_principal', hide: 'PASSWORD'},
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
