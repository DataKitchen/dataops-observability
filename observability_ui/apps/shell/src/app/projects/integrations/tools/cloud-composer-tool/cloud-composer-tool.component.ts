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
import { MatLegacySelectModule } from '@angular/material/legacy-select';
import { MatLegacyFormFieldModule } from '@angular/material/legacy-form-field';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'cloud-composer-tool',
  templateUrl: 'cloud-composer-tool.component.html',
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
export class GoogleCloudComposerToolComponent extends AbstractTool {
  static override _name = 'gcc';
  static override _displayName = 'Google Cloud Composer';
  static override _icon = 'cloud_composer';
  static override _type = 'POLLING';
  static override _image = 'docker.io/datakitchen/dk-poller-obs-agent';

  override readonly envList = [
    ...this.commonEnvs,
    { name: 'BASE64_ENCODED_SERVICE_ACCOUNT_STR', placeholder: '# the resulting string of your Base64 encoded service account JSON file', required: true },
    { name: 'COMPOSER_CLIENT_ID', placeholder: '# (version 1) the client ID of the Identity and Access Management proxy that protects the Airflow web server', required: true },
    { name: 'COMPOSER_WEBSERVER_ID', placeholder: '# (version 1) the webserver ID can be found in the instance as https://{webserver-id}.appspot.com', required: true },
    { name: 'COMPOSER_2_AUTH_SCOPE', placeholder: '', required: true },
    { name: 'COMPOSER_2_FLAG', placeholder: '', required: true },
    { name: 'COMPOSER_2_WEB_URL', placeholder: '# (version 2) the web URL of your Cloud Composer instance', required: true },
  ];

  // https://www.googleapis.com/auth/cloud-platform
  override envListForm = new FormGroup({
    ...this.commonEnvsForm.controls,

    ENABLED_PLUGINS: new FormControl('airflow_composer', Validators.required),

    BASE64_ENCODED_SERVICE_ACCOUNT_STR: new FormControl('', Validators.required),
    COMPOSER_CLIENT_ID: new FormControl('', Validators.required),
    COMPOSER_WEBSERVER_ID: new FormControl('', Validators.required),
    COMPOSER_2_AUTH_SCOPE: new FormControl('https://www.googleapis.com/auth/cloud-platform', Validators.required),
    COMPOSER_2_FLAG: new FormControl('True', Validators.required),
    COMPOSER_2_WEB_URL: new FormControl('', Validators.required),
  });

  protected override disableOnStart: FormControl<any>[] = [
    this.envListForm.controls['ENABLED_PLUGINS'],
    this.envListForm.controls['COMPOSER_2_AUTH_SCOPE'],
    this.envListForm.controls['COMPOSER_2_FLAG'],
  ];
}
