import { Directive, EventEmitter, Input, Output } from '@angular/core';
import { AbstractTemplating } from '../../templating';


@Directive()
export abstract class AbstractAction<RuleType = any> extends AbstractTemplating {
  @Input() expanded!: boolean;
  @Output() delete: EventEmitter<void> = new EventEmitter();

  // eslint-disable-next-line @typescript-eslint/no-empty-function, @typescript-eslint/no-unused-vars
  hydrateFromRule(rule: RuleType): void {}

  toJSON(): {action: string, action_args: any} {
    return {
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      action: this.type,
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      action_args: this.form.value,
    };
  }

  onDelete() {
    this.delete.emit();
  }
}
