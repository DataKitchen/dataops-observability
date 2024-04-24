import { Directive, Input, OnInit } from '@angular/core';
import { MatLegacyColumnDef as MatColumnDef } from '@angular/material/legacy-table';
import { BooleanInput, coerceBooleanProperty } from '@angular/cdk/coercion';

@Directive({
  selector: '[matColumnDef] ~ [toggleDisabled]', // <- sibling selector: makes `sortDisabled` valid only as a sibling of matColumnDef
})
export class ToggleDisabledDirective implements OnInit {
  @Input('toggleDisabled')
  get disabled(): boolean {
    return this._disabled;
  }

  set disabled(value: BooleanInput) {
    this._disabled = coerceBooleanProperty(value);
  }
  // eslint-disable-next-line @angular-eslint/no-input-rename
  private _disabled: boolean = false;

  columnName!: string;

  constructor(private elm: MatColumnDef) {
  }

  ngOnInit(): void {
    this.columnName = this.elm.name;
  }

}
