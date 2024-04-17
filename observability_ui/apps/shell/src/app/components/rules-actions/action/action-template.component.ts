import { Component, Input } from '@angular/core';
import { MatExpansionModule } from '@angular/material/expansion';
import { NgIf } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatLegacyButtonModule as MatButtonModule } from '@angular/material/legacy-button';
import { AbstractAction } from '../abstract-action.directive';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'action-template',
  templateUrl: 'action-template.component.html',
  styleUrls: [ 'action-template.component.scss' ],
  standalone: true,
  imports: [
    MatExpansionModule,
    NgIf,
    MatIconModule,
    MatButtonModule,
  ],
  // providers: [returnProvider(AbstractAction)]
})

export class ActionTemplateComponent {

  @Input() action: AbstractAction;
}
