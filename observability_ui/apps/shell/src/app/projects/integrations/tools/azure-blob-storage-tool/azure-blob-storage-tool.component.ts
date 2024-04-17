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
import { CustomValidators } from '@observability-ui/core';
import { MatLegacyCheckboxModule } from '@angular/material/legacy-checkbox';
import { MatLegacySelectModule } from '@angular/material/legacy-select';
import { MatLegacyFormFieldModule } from '@angular/material/legacy-form-field';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'azure-blob-storage-tool',
  templateUrl: 'azure-blob-storage-tool.component.html',
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
export class AzureBlobStorageToolComponent extends AbstractTool {
  static override _name = 'blob_storage';
  static override _displayName = 'Azure Blob Storage';
  static override _icon = 'blob_storage';
  static override _type = 'EVENTS';
  static override _image = 'docker.io/datakitchen/dk-event-hubs-obs-agent';

  override readonly envList = [
    ...this.commonEnvs,
    { name: 'EVENT_HUB_CONN_STR', placeholder: '# the connection string for Azure Event Hubs', required: true },
    { name: 'EVENT_HUB_NAME', placeholder: '# the name of your Azure Event Hubs instance (not the namespace)', required: true },
    { name: 'AZURE_STORAGE_CONN_STR', placeholder: '# the connection string for your Azure storage', required: false },
    { name: 'BLOB_CONTAINER_NAME', placeholder: '# the name of your Blob storage container', required: false },
  ];

  override envListForm = new FormGroup({
    ...this.commonEnvsForm.controls,

    ENABLED_PLUGINS: new FormControl('blob_event_handler', Validators.required),
    EVENT_HUB_CONN_STR: new FormControl('', Validators.required),
    EVENT_HUB_NAME: new FormControl('', Validators.required),

    USE_CHECKPOINT_STORE: new FormControl(false),
    AZURE_STORAGE_CONN_STR: new FormControl(''),
    BLOB_CONTAINER_NAME: new FormControl(''),
  }, [
    CustomValidators.requiredIf('AZURE_STORAGE_CONN_STR', (control) => this.requiredIfCheck('AZURE_STORAGE_CONN_STR', control as FormGroup)),
    CustomValidators.requiredIf('BLOB_CONTAINER_NAME', (control) => this.requiredIfCheck('BLOB_CONTAINER_NAME', control as FormGroup)),
  ]);

  protected override hidingRules = [
    {when: 'USE_CHECKPOINT_STORE', equals: false, hide: 'AZURE_STORAGE_CONN_STR'},
    {when: 'USE_CHECKPOINT_STORE', equals: false, hide: 'BLOB_CONTAINER_NAME'},
  ];
  protected override disableOnStart: FormControl<any>[] = [
    this.envListForm.controls['ENABLED_PLUGINS'],
  ];

  private requiredIfCheck(variable: string, control: FormGroup): boolean {
    const required = control.controls['USE_CHECKPOINT_STORE'].value === true;
    this.envList.find(({ name }) => name === variable).required = required;
    return required;
  }
}
