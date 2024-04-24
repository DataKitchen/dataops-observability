import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { BreadcrumbItem } from './breadcrumb.model';


@Component({
  selector: 'breadcrumb',
  templateUrl: 'breadcrumb.component.html',
  styleUrls: [ 'breadcrumb.component.scss' ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BreadcrumbComponent {

  @Input() items!: BreadcrumbItem[];

}
