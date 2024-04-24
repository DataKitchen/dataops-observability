import { AfterViewInit, Directive, ElementRef, Input } from '@angular/core';

@Directive({
  selector: '[headerLabel]',
})
export class HeaderLabelDirective implements AfterViewInit {
  @Input()
  headerLabel!: string;

  textContent!: string;

  constructor(public elementRef: ElementRef<HTMLElement>) {
  }

  ngAfterViewInit(): void {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    this.textContent = this.elementRef.nativeElement.textContent.trim();
  }
}
