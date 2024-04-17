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
import { MatLegacyFormFieldModule } from '@angular/material/legacy-form-field';
import { MatLegacySelectModule } from '@angular/material/legacy-select';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'talend-tool',
  templateUrl: 'talend-tool.component.html',
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
export class TalendToolComponent extends AbstractTool {
  static override _name = 'talend';
  static override _displayName = 'Talend';
  static override _icon = 'talend';
  static override _type = 'POLLING';
  static override _image = 'docker.io/datakitchen/dk-poller-obs-agent';

  override readonly envList = [
    ...this.commonEnvs,
    { name: 'TALEND_BASE_API_URL', placeholder: '# the URL for the Talend API', required: true },
    { name: 'TALEND_TOKEN', placeholder: '# the token of your Talend instance', required: true },
  ];

  override envListForm = new FormGroup({
    ...this.commonEnvsForm.controls,

    ENABLED_PLUGINS: new FormControl('talend_management_console', Validators.required),
    TALEND_BASE_API_URL: new FormControl('', Validators.required),
    TALEND_TOKEN: new FormControl('', Validators.required),
  });

  protected override disableOnStart: FormControl<any>[] = [
    this.envListForm.controls['ENABLED_PLUGINS'],
  ];
}
