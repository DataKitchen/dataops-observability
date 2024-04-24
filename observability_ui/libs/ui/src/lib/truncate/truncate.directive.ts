import { Directive, ElementRef, OnDestroy, OnInit } from '@angular/core';
import { BehaviorSubject, Observable, Subscription } from 'rxjs';

@Directive({
  selector: '[truncate]'
})
export class TruncateDirective implements OnInit, OnDestroy {
  subscriptions: Subscription[];

  public truncated = new BehaviorSubject<boolean>(false);

  private elementResizeObserver = new Observable<DOMRect>(observer => {
    new ResizeObserver(() => {
      observer.next(this.element.nativeElement.getBoundingClientRect());
    }).observe(this.element.nativeElement);
  });


  constructor(private element: ElementRef) {
    const truncateSub = this.truncated.subscribe((value) => {
      value ? this.element.nativeElement.classList.add('truncated') : this.element.nativeElement.classList.remove('truncated');
    });

    const resizeSub = this.elementResizeObserver.subscribe(() => {
      this.truncated.next(this.isWidthOverflowed() || this.isHeightOverflowed());
    });

    this.subscriptions = [ truncateSub, resizeSub ];
  }

  ngOnInit() {
    this.element.nativeElement.style.maxWidth = '100%';
    this.element.nativeElement.style.wordBreak = 'break-all';
    this.element.nativeElement.style.whiteSpace = 'nowrap';
  }

  private isWidthOverflowed(): boolean {
    const { clientWidth, scrollWidth } = this.element.nativeElement as HTMLElement || {};
    return clientWidth < scrollWidth;
  }

  private isHeightOverflowed(): boolean {
    const { clientHeight, scrollHeight } = this.element.nativeElement as HTMLElement || {};
    return clientHeight < scrollHeight;
  }

  ngOnDestroy() {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }
}
