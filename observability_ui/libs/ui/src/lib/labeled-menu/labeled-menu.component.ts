import { Component, Input } from '@angular/core';

@Component({
  selector: 'labeled-menu',
  templateUrl: 'labeled-menu.component.html',
  styleUrls: [ 'labeled-menu.component.scss' ],
})
export class LabeledMenuComponent {

  @Input()
  public label!: string;

  @Input()
  public showDropDownArrow!: boolean;

  @Input()
  public id!: string;

  @Input()
  public disabled!: boolean;

}
