import { AfterViewInit, Directive, ElementRef, Input } from '@angular/core';

/**
 *
 * Add this directive to an element in order to get
 * its reference in a component using `@ViewChild[ren]`
 * decorators. Same way it would be done using a `#id`
 * reference and then `@ViewChild('id')`. However this
 * is handy when, for example, a list of dynamic
 * elements needs to be referenced.
 *
 *
 * in template
 * ```html
 * <div *ngFor="let i of items" element-ref> {{i}} </div>
 * ```
 *
 * in component
 * ```typescript
 * @ViewChildren(ElementRefDirective) elements: QueryList;
 * ```
 */
@Directive({
  selector: '[element-ref]',
  standalone: true,
})
export class ElementRefDirective implements AfterViewInit {
  @Input() scrollIntoView!: boolean;
  @Input() scrollIntoViewOptions: {
    behaviour: 'smooth'|'instant'|'auto';
    block: 'start'|'center'|'end'|'nearest';
    inline: 'start'|'center'|'end'|'nearest';
  } = {
    behaviour: 'smooth',
    block: 'center',
    inline: 'nearest',
  };

  constructor(public elm: ElementRef) {}

  ngAfterViewInit() {
    if (this.scrollIntoView) {
      this.elm.nativeElement.scrollIntoView(this.scrollIntoViewOptions);
    }
  }
}
