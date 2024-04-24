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
  selector: 'ssis-tool',
  templateUrl: 'ssis-tool.component.html',
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
export class SSISToolComponent extends AbstractTool {
  static override _name = 'ssis';
  static override _displayName = 'Microsoft SSIS';
  static override _icon = 'mssql';
  static override _image = 'docker.io/datakitchen/observability-agent-trial';
  static override _version = 'production';

  private readonly defaultValues = {
    port: '1433',
    pollingInterval: '30'
  };

  override readonly envList = [
    { name: 'AGENT_TYPE', tpl: 'agent_type', placeholder: '' },
    { name: 'AGENT_KEY', tpl: 'agent_key', placeholder: '# assigns the identifier of the agent', required: true },
    { name: 'DK_API_URL', tpl: 'observability_base_url', placeholder: '# the URL to the Observability API', required: true },
    { name: 'DK_API_KEY', tpl: 'observability_service_account_key', placeholder: '# an API key for the Observability project', required: true },
    { name: 'DB_HOST', tpl: 'ssis_db_host', placeholder: '# the URL of the SSIS instance', required: true },
    { name: 'DB_USER', tpl: 'ssis_db_user', placeholder: '# the username for an SSIS account', required: true },
    { name: 'DB_PASSWORD', tpl: 'ssis_db_password', placeholder: '# the password for an SSIS account', required: true },
    { name: 'DB_PORT', tpl: 'ssis_db_port', placeholder: `# the port of the SSIS instance (default: ${this.defaultValues.port})`, default: this.defaultValues.port },
    { name: 'POLLING_INTERVAL', tpl: 'ssis_polling_interval', placeholder: `# the cadence at which the agent polls for information (default: ${this.defaultValues.pollingInterval})`, default: this.defaultValues.pollingInterval },
  ];

  override envListForm = new FormGroup({
    AGENT_TYPE: new FormControl('ssis', Validators.required),
    AGENT_KEY: new FormControl('', Validators.required),
    DK_API_URL: new FormControl('', Validators.required),
    DK_API_KEY: new FormControl('', Validators.required),
    DB_HOST: new FormControl('', Validators.required),
    DB_USER: new FormControl('', Validators.required),
    DB_PASSWORD: new FormControl('', Validators.required),
    DB_PORT: new FormControl(this.defaultValues.port),
    POLLING_INTERVAL: new FormControl(this.defaultValues.pollingInterval, Validators.min(30)),
    DOCKER_TAG: new FormControl('', [ Validators.required ]),
    DEFAULT_DEPLOYMENT_MODE: new FormControl('', [ Validators.required, CustomValidators.oneOf([ 'docker', 'kubernetes' ]) ]),
  });

  protected override disableOnStart: FormControl<any>[] = [
    this.envListForm.controls['AGENT_TYPE'],
  ];
}
