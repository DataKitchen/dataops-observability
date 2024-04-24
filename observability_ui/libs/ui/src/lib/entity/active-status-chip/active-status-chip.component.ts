import { ChangeDetectionStrategy, Component, Input } from '@angular/core';


@Component({
  selector: 'active-status-chip',
  templateUrl: 'active-status-chip.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ActiveStatusChipComponent {

  @Input() active!: boolean;
}
