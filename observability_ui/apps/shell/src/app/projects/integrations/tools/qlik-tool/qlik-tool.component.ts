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
import { listEnvVariableFormatter } from '@observability-ui/core';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'qlik-tool',
  templateUrl: 'qlik-tool.component.html',
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
export class QlikToolComponent extends AbstractTool {
  static override _name = 'qlik';
  static override _displayName = 'Qlik';
  static override _icon = 'qlik';
  static override _image = 'docker.io/datakitchen/observability-agent-trial';
  static override _version = 'production';

  private readonly defaultValues = {
    period: '30.0',
    timeout: '120.0',
  };

  override readonly envList = [
    { name: 'AGENT_TYPE', tpl: 'agent_type', placeholder: '' },
    { name: 'AGENT_KEY', tpl: 'agent_key', placeholder: '# assigns the identifier of the agent', required: true },
    { name: 'DK_API_URL', tpl: 'observability_base_url', placeholder: '# the URL to the Observability API', required: true },
    { name: 'DK_API_KEY', tpl: 'observability_service_account_key', placeholder: '# an API key for the Observability project', required: true },
    { name: 'TENANT', tpl: 'qlik_tenant', placeholder: '# the tenant ID of the Qlik Cloud account', required: true },
    { name: 'API_KEY', tpl: 'qlik_api_key', placeholder: '# an API key for the Qlik Cloud account', required: true },
    {
      name: 'APPS',
      tpl: 'qlik_apps',
      placeholder: '# comma-separated list of app names to monitor',
      formatter: listEnvVariableFormatter,
    },
    { name: 'PERIOD', tpl: 'DK_QLIK_PERIOD', placeholder: `# the cadence at which the agent polls for information (default: ${this.defaultValues.period})`, default: this.defaultValues.period },
    { name: 'TIMEOUT', tpl: 'DK_QLIK_TIMEOUT', placeholder: `# the timeout for requests made by the agent (default: ${this.defaultValues.timeout}`, default: this.defaultValues.timeout },
  ];

  override envListForm = new FormGroup({
    AGENT_TYPE: new FormControl('qlik', Validators.required),
    AGENT_KEY: new FormControl('', Validators.required),
    DK_API_URL: new FormControl('', Validators.required),
    DK_API_KEY: new FormControl('', Validators.required),
    TENANT: new FormControl('', Validators.required),
    API_KEY: new FormControl('', Validators.required),
    APPS: new FormControl(''),
    PERIOD: new FormControl(this.defaultValues.period, Validators.min(5)),
    TIMEOUT: new FormControl(this.defaultValues.timeout, Validators.min(15)),
    DOCKER_TAG: new FormControl('', [ Validators.required ]),
    DEFAULT_DEPLOYMENT_MODE: new FormControl('', [ Validators.required, CustomValidators.oneOf([ 'docker', 'kubernetes' ]) ]),
  });

  protected override disableOnStart: FormControl<any>[] = [
    this.envListForm.controls['AGENT_TYPE'],
  ];
}
