import { Directive, Input, OnChanges, SimpleChanges } from '@angular/core';
import { ComponentType } from '@angular/cdk/overlay';
import { FormControl, FormGroup } from '@angular/forms';

@Directive()
export abstract class AbstractTemplating implements OnChanges {
  static label: string;
  static icon: string;
  static labelTpl: ComponentType<any>;
  static alert: string;
  static alertIcon: string;

  abstract version: string;

  static _type: string;

  get type() {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    return this.constructor._type;
  }

  get labelFromInstance() {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    return this.constructor.label;
  }

  @Input() editMode: boolean;
  @Input() data: any;

  abstract form: FormControl | FormGroup;

  abstract toJSON(): object;

  ngOnChanges({data}: SimpleChanges) {
    if (data?.currentValue) {
      this.parse(data.currentValue);
    }
  }

  parse(data: any) {
    this.form.patchValue(data);
  }
}
