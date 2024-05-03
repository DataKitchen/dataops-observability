import { Component } from '@angular/core';
import { AbstractTool } from '../abstract-tool.directive';
import { MatIconModule } from '@angular/material/icon';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatLegacyButtonModule } from '@angular/material/legacy-button';
import { ServiceKeyFormComponent } from '../../service-key-form/service-key-form.component';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AlertComponent, CodeSnippetComponent, DkTooltipModule, TextFieldModule } from '@observability-ui/ui';
import { RouterModule } from '@angular/router';
import { MatLegacyCheckboxModule } from '@angular/material/legacy-checkbox';
import { MatLegacySelectModule } from '@angular/material/legacy-select';
import { MatLegacyFormFieldModule } from '@angular/material/legacy-form-field';
import { CustomValidators } from '@observability-ui/core';
import { listEnvVariableFormatter } from '@observability-ui/core';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'azure-functions-tool',
  templateUrl: 'azure-synapse-pipelines-tool.component.html',
  styleUrls: [ '../tools-common.scss' ],
  imports: [
    CommonModule,
    RouterModule,
    ReactiveFormsModule,

    MatIconModule,
    MatExpansionModule,
    MatLegacyButtonModule,
    MatLegacyCheckboxModule,
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
export class AzureSynapsePipelinesToolComponent extends AbstractTool {
  static override _name = 'azure_synapse_pipelines';
  static override _displayName = 'Azure Synapse';
  static override _icon = 'azure_synapse_pipelines';
  static override _image = 'docker.io/datakitchen/dataops-observability-agents';
  static override _version = 'production';

  private readonly defaultValues = {
    period: '5.0'
  };

  override readonly envList = [
    { name: 'AGENT_TYPE', tpl: 'agent_type', placeholder: '' },
    { name: 'AGENT_KEY', tpl: 'agent_key', placeholder: '# assigns the identifier of the agent', required: true },
    { name: 'DK_API_URL', tpl: 'observability_base_url', placeholder: '# the URL to the Observability API', required: true },
    { name: 'DK_API_KEY', tpl: 'observability_service_account_key', placeholder: '# an API key for the Observability project', required: true },
    { name: 'TENANT_ID', tpl: 'auth_azure_tenant_id', placeholder: '# the Directory (tenant) ID of the service principal', required: true },
    { name: 'CLIENT_ID', tpl: 'auth_azure_client_id', placeholder: '# the Application (client) ID of the service principal', required: true },
    { name: 'CLIENT_SECRET', tpl: 'auth_azure_client_secret', placeholder: '# the client secret value created during the setup of the service principal', required: true },
    { name: 'WORKSPACE_NAME', tpl: 'synapse_analytics_workspace_name', placeholder: '# the name of your Azure Synapse workspace', required: true },
    { name: 'SUBSCRIPTION_ID', tpl: 'synapse_analytics_subscription_id', placeholder: '# the ID of the subscription where the resource group and Synapse workspace exist' },
    { name: 'RESOURCE_GROUP_NAME', tpl: 'synapse_analytics_resource_group_name', placeholder: '# the name of the resource group where your Azure Synapse workspace exists' },
    {
      name: 'PIPELINES_FILTER',
      tpl: 'synapse_analytics_pipelines_filter',
      placeholder: '# comma-separated list of pipeline names to monitor',
      formatter: listEnvVariableFormatter,
    },
    { name: 'PERIOD', tpl: 'DK_SYNAPSE_ANALYTICS_PERIOD', placeholder: `# the cadence at which the agent polls for information (default: ${this.defaultValues.period})`, default: this.defaultValues.period },
  ];

  override envListForm = new FormGroup({
    AGENT_TYPE: new FormControl('synapse_analytics', Validators.required),
    AGENT_KEY: new FormControl('', Validators.required),
    DK_API_URL: new FormControl('', Validators.required),
    DK_API_KEY: new FormControl('', Validators.required),
    TENANT_ID: new FormControl('', Validators.required),
    CLIENT_ID: new FormControl('', Validators.required),
    CLIENT_SECRET: new FormControl('', Validators.required),
    WORKSPACE_NAME: new FormControl('', Validators.required),
    SUBSCRIPTION_ID: new FormControl(''),
    RESOURCE_GROUP_NAME: new FormControl(''),
    PIPELINES_FILTER: new FormControl(''),
    PERIOD: new FormControl(this.defaultValues.period, Validators.min(5)),
    DOCKER_TAG: new FormControl('', [ Validators.required ]),
    DEFAULT_DEPLOYMENT_MODE: new FormControl('', [ Validators.required, CustomValidators.oneOf([ 'docker', 'kubernetes' ]) ]),
  });

  protected override disableOnStart: FormControl<any>[] = [
    this.envListForm.controls['AGENT_TYPE'],
  ];
}
