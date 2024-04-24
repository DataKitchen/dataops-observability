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
import { MatLegacyFormFieldModule } from '@angular/material/legacy-form-field';
import { MatLegacySelectModule } from '@angular/material/legacy-select';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'fivetran-logs-tool',
  templateUrl: 'fivetran-logs-tool.component.html',
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
export class FivetranLogConnectorToolComponent extends AbstractTool {
  static override _name = 'fivetran';
  static override _displayName = 'Fivetran Log Connector';
  static override _icon = 'fivetran';
  static override _type = 'POLLING';
  static override _image = 'docker.io/datakitchen/dk-poller-obs-agent';

  override readonly envList = [
    ...this.commonEnvs,
    { name: 'FIVETRAN_DB_LOOKUP', placeholder: '# the max lookback period', required: true },
    { name: 'FIVETRAN_DB_SERVER_HOSTNAME', placeholder: '# the hostname of the Databrick SQL interface. For example, dbc-XXXXXX-d6e7.cloud.databricks.com', required: true },
    { name: 'FIVETRAN_DB_HTTP_PATH', placeholder: '# the HTTP path to either a Databricks SQL endpoint or Databricks Runtime interactive cluster', required: true },
    { name: 'FIVETRAN_DB_LOG_SCHEMA', placeholder: '# the schema in Databricks where the Fivetran log connector sends logs', required: true },
    { name: 'FIVETRAN_DB_PERSONAL_ACCESS_TOKEN', placeholder: '# the Databricks personal access token that has access to the Fivetran log schema', required: true },
  ];

  override envListForm = new FormGroup({
    ...this.commonEnvsForm.controls,

    ENABLED_PLUGINS: new FormControl('fivetran_log_to_databricks', Validators.required),
    FIVETRAN_DB_LOOKUP: new FormControl('', Validators.required),
    FIVETRAN_DB_SERVER_HOSTNAME: new FormControl('', Validators.required),
    FIVETRAN_DB_HTTP_PATH: new FormControl('', Validators.required),
    FIVETRAN_DB_LOG_SCHEMA: new FormControl('', Validators.required),
    FIVETRAN_DB_PERSONAL_ACCESS_TOKEN: new FormControl('', Validators.required),
  });

  protected override disableOnStart: FormControl<any>[] = [
    this.envListForm.controls['ENABLED_PLUGINS'],
  ];
}
