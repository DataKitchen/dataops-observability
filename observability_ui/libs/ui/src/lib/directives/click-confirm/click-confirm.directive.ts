import { Directive, ElementRef, EventEmitter, Input, NgModule, OnInit, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatLegacySnackBar as MatSnackBar } from '@angular/material/legacy-snack-bar';

@Directive({
  selector: '[clickConfirm]',
})
export class ClickConfirmDirective implements OnInit {

  @Output() clickConfirm = new EventEmitter();
  @Input() label: string = 'Click again to confirm action.';

  private hijackClick = true;
  private timeout: number = 2000;
  private timer!: any;

  constructor(
    private elm: ElementRef,
    private snack: MatSnackBar,
  ) {}

  ngOnInit() {

    this.elm.nativeElement.addEventListener('click', (...args: unknown[]) => {

      if (this.hijackClick) {
        this.snack.open(this.label, undefined, {
          duration: this.timeout,
        });

        this.hijackClick = false;

        if (this.timer) {
          // clears old timers
          clearTimeout(this.timer);
        }

        this.timer = setTimeout(() => {
          this.hijackClick = true;
        }, this.timeout);

      } else {
        this.clickConfirm.next(args);
        clearTimeout(this.timer);
      }

    });

  }

}

@NgModule({
  imports: [ CommonModule ],
  declarations: [ ClickConfirmDirective ],
  exports: [ ClickConfirmDirective ],
})
export class ClickConfirmDirectiveModule {
}
