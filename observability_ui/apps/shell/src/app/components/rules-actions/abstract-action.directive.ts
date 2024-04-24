import { Directive, EventEmitter, Input, Output } from '@angular/core';
import { Rule } from './rule.model';
import { AbstractTemplating } from './abstract-templating.directive';
import { AbstractRule } from './abstract.rule';

@Directive()
export abstract class AbstractAction extends AbstractTemplating {

  @Input() expanded: boolean;
  @Output() delete: EventEmitter<void> = new EventEmitter();

  // eslint-disable-next-line @typescript-eslint/no-empty-function, @typescript-eslint/no-unused-vars
  hydrateFromRule(rule: AbstractRule): void {}

  toJSON(): Pick<Rule, 'action' | 'action_args'> {
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
