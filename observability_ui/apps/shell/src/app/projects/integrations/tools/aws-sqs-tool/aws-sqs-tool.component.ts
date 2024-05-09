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

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'aws-sqs-tool',
  templateUrl: 'aws-sqs-tool.component.html',
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
export class AWSSQSToolComponent extends AbstractTool {
  static override _name = 'sqs';
  static override _displayName = 'Amazon S3';
  static override _icon = 'aws_s3';
  static override _type = 'EVENTS';
  static override _image = 'docker.io/datakitchen/dk-aws-sqs-obs-agent';

  override readonly envList = [
    ...this.commonEnvs,
    { name: 'ACCESS_KEY', placeholder: '# the access key for your AWS account', required: true },
    { name: 'SECRET_KEY', placeholder: '# the secret key of your AWS account', required: true },
    { name: 'AWS_DEFAULT_REGION', placeholder: '# the default region of your AWS account', required: true },
    { name: 'SQS_QUEUE_NAME', placeholder: '# name of the AWS SQS queue', required: true },
    { name: 'SESSION_TOKEN', placeholder: '# required if you\'re using temporary credentials', required: false },
  ];

  override envListForm = new FormGroup({
    ...this.commonEnvsForm.controls,

    ENABLED_PLUGINS: new FormControl('aws_s3_event_handler', Validators.required),
    ACCESS_KEY: new FormControl('', Validators.required),
    SECRET_KEY: new FormControl('', Validators.required),
    AWS_DEFAULT_REGION: new FormControl('', Validators.required),
    SQS_QUEUE_NAME: new FormControl('', Validators.required),
    SESSION_TOKEN: new FormControl(''),
  });

  protected override disableOnStart: FormControl<any>[] = [
    this.envListForm.controls['ENABLED_PLUGINS'],
  ];
}
