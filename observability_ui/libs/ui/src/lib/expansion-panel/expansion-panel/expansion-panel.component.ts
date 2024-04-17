import { Component, Input } from '@angular/core';

@Component({
  selector: 'expansion-panel',
  templateUrl: 'expansion-panel.component.html' ,
  styleUrls: [ 'expansion-panel.component.scss' ],
})
export class ExpansionPanelComponent {
  @Input() open: boolean = false;

}
