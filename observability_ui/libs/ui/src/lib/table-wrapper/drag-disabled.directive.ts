import { Directive, Input, OnInit } from '@angular/core';
import { MatLegacyColumnDef as MatColumnDef } from '@angular/material/legacy-table';

@Directive({
  selector: '[matColumnDef] ~ [dragDisabled]', // <- sibling selector: makes `sortDisabled` valid only as a sibling of matColumnDef
})
export class DragDisabledDirective implements OnInit {
  // eslint-disable-next-line @angular-eslint/no-input-rename
  @Input('dragDisabled')
  disabled!: boolean;

  columnName!: string;

  constructor(private elm: MatColumnDef) {
  }

  ngOnInit(): void {

    this.columnName = this.elm.name;

    // force boolean value of matSortDisable so that
    // when used such as
    // <ng-container matColumnDef="columnName" matSortDisable></ng-container>
    // will be true
    // i.e. it's a shorthand for matSortDisabled="true"

    if ((this.disabled as unknown as string) === '') {
      this.disabled = true;
    }
  }

}
