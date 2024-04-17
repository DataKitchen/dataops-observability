import { Component, Input } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { DkTooltipModule } from '@observability-ui/ui';
import { LowerCasePipe, NgIf, TitleCasePipe } from '@angular/common';
import { TranslationModule } from '@observability-ui/translate';
import { ComponentType } from '@observability-ui/core';
import { GetToolClassPipe } from '../../integrations/tool-selector/get-tool-class.pipe';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'component-icon',
  template: `

    <mat-icon
      [dkTooltip]="(tool| getToolClass)?._displayName || (componentTypeTag[type] | titlecase) "
      class="icon-size-{{size}}"
      [svgIcon]="(tool| getToolClass)?._icon || (type | lowercase)">
    </mat-icon>

  `,
  styles: [`
    :host {
      display: flex;
    }
  `],
  standalone: true,
  imports: [
    MatIconModule,
    DkTooltipModule,
    NgIf,
    LowerCasePipe,
    TitleCasePipe,
    TranslationModule,
    GetToolClassPipe,
  ]
})
export class ComponentIconComponent {

  componentTypeTag: { [key: string]: string} = {
    [ComponentType.BatchPipeline]: 'batch pipeline',
    [ComponentType.StreamingPipeline]: 'streaming pipeline',
    [ComponentType.Server]: 'server',
    [ComponentType.Dataset]: 'dataset',
  };

  @Input() size: number = 16;
  @Input() tool: string;
  @Input() type: ComponentType;
}
