import { ChangeDetectionStrategy, Component, Input } from '@angular/core';


@Component({
  selector: 'entity-list-placeholder',
  styleUrls: [ 'entity-list-placeholder.component.scss' ],
  templateUrl: 'entity-list-placeholder.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EntityListPlaceholderComponent {

  @Input() entity!: string;
  @Input() loading!: boolean;
  @Input() total!: number;
  @Input() hasFilters!: boolean;
}
