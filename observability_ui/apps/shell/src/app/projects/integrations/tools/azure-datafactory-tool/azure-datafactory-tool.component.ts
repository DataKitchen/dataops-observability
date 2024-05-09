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
import { CustomValidators, listEnvVariableFormatter } from '@observability-ui/core';
import { MatLegacyCheckboxModule } from '@angular/material/legacy-checkbox';
import { MatLegacySelectModule } from '@angular/material/legacy-select';
import { MatLegacyFormFieldModule } from '@angular/material/legacy-form-field';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'azure-datafactory-tool',
  templateUrl: 'azure-datafactory-tool.component.html',
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
export class AzureDataFactoryToolComponent extends AbstractTool {
  static override _name = 'data_factory';
  static override _displayName = 'Azure Data Factory';
  static override _icon = 'data_factory';
  static override _image = 'docker.io/datakitchen/dataops-observability-agents';
  static override _version = 'production';

  private readonly defaultValues = {
    startingPosition: '-1',
  };

  override readonly envList = [
    { name: 'AGENT_TYPE', tpl: 'agent_type', placeholder: '' },
    { name: 'MESSAGE_TYPES', tpl: 'azure_eventhub_message_types', placeholder: '', formatter: listEnvVariableFormatter },
    { name: 'AGENT_KEY', tpl: 'agent_key', placeholder: '# assigns the identifier of the agent', required: true },
    { name: 'DK_API_URL', tpl: 'observability_base_url', placeholder: '# the base API URL for Observability', required: true },
    { name: 'DK_API_KEY', tpl: 'observability_service_account_key', placeholder: '# an API key for the Observability project', required: true },
    { name: 'NAME', tpl: 'azure_eventhub_name', placeholder: '# the name of your Azure Event Hubs instance', required: true },
    { name: 'CONNECTION_STRING', tpl: 'azure_eventhub_connection_string', placeholder: '# the connection string for Event Hubs', required: true },
    { name: 'STARTING_POSITION', tpl: 'azure_eventhub_starting_position', placeholder: `# the event position from which the agent starts receiving (default: ${this.defaultValues.startingPosition})`, default: this.defaultValues.startingPosition },
    { name: 'BLOB_NAME', tpl: 'azure_blob_name', placeholder: '# the name of your Blob storage container' },
  ];

  override envListForm = new FormGroup({
    AGENT_TYPE: new FormControl('eventhubs', Validators.required),
    MESSAGE_TYPES: new FormControl('ADF', Validators.required),
    AGENT_KEY: new FormControl('', Validators.required),
    DK_API_URL: new FormControl('', Validators.required),
    DK_API_KEY: new FormControl('', Validators.required),
    NAME: new FormControl('', Validators.required),
    CONNECTION_STRING: new FormControl('', Validators.required),
    STARTING_POSITION: new FormControl(''),
    BLOB_NAME: new FormControl(''),
    DOCKER_TAG: new FormControl('', [ Validators.required ]),
    DEFAULT_DEPLOYMENT_MODE: new FormControl('', [ Validators.required, CustomValidators.oneOf([ 'docker', 'kubernetes' ]) ]),
  });

  protected override disableOnStart: FormControl<any>[] = [
    this.envListForm.controls['AGENT_TYPE'],
    this.envListForm.controls['MESSAGE_TYPES'],
  ];
}
