import { ComponentRef, Directive, EventEmitter, Input, OnChanges, OnInit, Output, ViewContainerRef } from '@angular/core';
import { ComponentType } from '@angular/cdk/overlay';

@Directive({
  // eslint-disable-next-line @angular-eslint/directive-selector
  selector: '[dynamicComponentOutlet]',
})
export class DynamicComponentOutletDirective<T = any> implements OnChanges, OnInit {
  @Input('dynamicComponentOutlet') component!: ComponentType<T>;
  @Input() dynamicComponentOutletOptions: object = {};

  @Input() dynamicComponentOutletOutputs: string[] = [];

  @Output() outputs: EventEmitter<any> = new EventEmitter<any>();

  ref!: ComponentRef<T>;

  constructor(protected view: ViewContainerRef) {
  }

  ngOnInit() {
    this.createComponent();
  }

  ngOnChanges(): void {

    Object.entries(this.dynamicComponentOutletOptions).forEach(([ name, value ]) => {
      this.ref?.setInput(name, value);
    });

  }

  private createComponent() {
    if (this.component) {
      this.view.clear();
      this.ref = this.view.createComponent(this.component);
      Object.entries(this.dynamicComponentOutletOptions).forEach(([ name, value ]) => {
        this.ref.setInput(name, value);
      });

      this.dynamicComponentOutletOutputs
        .forEach((output) => {
          // eslint-disable-next-line @typescript-eslint/ban-ts-comment
          // @ts-ignore
          if (this.isEventEmitter(this.ref.instance[output])) {
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            this.ref.instance[output].subscribe((args) => {
              this.outputs.emit({ output: args });
            });
          }
        });
    }
  }

  private isEventEmitter(c: unknown): c is EventEmitter<any> {
    return c instanceof EventEmitter;
  }

}
