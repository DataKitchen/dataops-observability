import { Component, Input } from '@angular/core';

@Component({
  selector: 'details-header',
  templateUrl: 'details-header.component.html',
  styleUrls: [ 'details-header.component.scss' ],
})
export class DetailsHeaderComponent {
  @Input() title!: string;
  @Input() subTitle!: string;
  @Input() backLink!: string | string[];
  @Input() backLinkTitle!: string;
}
