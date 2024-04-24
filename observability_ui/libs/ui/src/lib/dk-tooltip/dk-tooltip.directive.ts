/* eslint-disable @angular-eslint/no-input-rename */
import { Directive, ElementRef, Input, NgZone, OnDestroy, OnInit, TemplateRef, ViewContainerRef, Renderer2, ChangeDetectorRef, Optional } from '@angular/core';
import { ComponentPortal } from '@angular/cdk/portal';
import { Overlay, OverlayRef, ScrollDispatcher, ConnectedPosition } from '@angular/cdk/overlay';
import { Subject, tap } from 'rxjs';
import { filter, takeUntil } from 'rxjs/operators';
import { DkTooltipComponent } from './dk-tooltip.component';
import { getOppositePosition, Placement, POSITIONS } from './dk-tooltip.model';
import { ClickListenerService } from './click-listener.service';
import { TruncateDirective } from '../truncate/truncate.directive';

@Directive({
  selector: '[dkTooltip]',
})
export class DkTooltipDirective implements OnInit, OnDestroy {
  private _content!: TemplateRef<any> | string;

  @Input('dkTooltip') set content(value: TemplateRef<any> | string) {
    this._content = value;
    if (!this._content) {
      this.disabled = true;
    } else {
      this.disabled = false;
    }
  }

  get content(): TemplateRef<any> | string {
    return this._content;
  }

  @Input('dkTooltipTrigger')
  trigger: 'click' | 'hover' = 'hover';

  @Input('dkTooltipType')
  type: 'dropdown' | 'tooltip' = 'tooltip';

  @Input('dkTooltipPlacement')
  placement: Placement = 'bottom';

  @Input('dkTooltipClass')
  tooltipClass: string = '';

  private _showArrow: boolean = true;
  @Input('dkTooltipShowArrow') set showArrow(value: boolean) {
    if (this._showArrow !== value) {
      this._showArrow = !!value;
      if (this.instance) {
        this.instance.showArrow = this._showArrow;
        this.instance._markForCheck();
      }
    }
  }

  get showArrow(): boolean {
    return this._showArrow;
  }

  private _disabled: boolean = false;
  @Input('dkTooltipDisabled') set disabled(value: boolean) {
    this._disabled = value;
    if (this._disabled && this.isOpen) {
      this.hide();
    }
  }

  get disabled(): boolean {
    return this._disabled;
  }

  portal!: ComponentPortal<DkTooltipComponent>;

  private overlayRef!: OverlayRef;
  private instance!: DkTooltipComponent;
  private destroyed$: Subject<void> = new Subject<void>();
  private isOpen!: boolean;
  private unregisterListenerFunction!: () => void;

  constructor(
    private _overlay: Overlay,
    private viewContainerRef: ViewContainerRef,
    private _scrollDispatcher: ScrollDispatcher,
    private _elementRef: ElementRef,
    private ngZone: NgZone,
    private clickListenerService: ClickListenerService,
    private renderer: Renderer2,
    private changeDetector: ChangeDetectorRef,
    @Optional() private truncate: TruncateDirective,
  ) {
    if (this.truncate) {
      this.truncate.truncated.pipe(
        takeUntil(this.destroyed$),
        tap((truncated) => this._disabled = !truncated)
      ).subscribe();
    }
  }

  ngOnInit(): void {
    const listeners: Array<() => void> = [];

    if (this.type === 'dropdown') {
      this.placement = 'bottom';
    }

    if (this.trigger === 'click') {
      listeners.push(
        this.renderer.listen(this._elementRef.nativeElement, 'click', () => {
          if (this.isOpen) {
            return this.hide();
          }
          return this.show();
        }),
      );

      this.clickListenerService.onClick
        .pipe(
          // only if this tooltip is already open
          filter(() => this.isOpen),
          // exclude clicks outside the element where this directive is used
          filter(($event) => {
            let hasDifferentTarget = $event.target !== this._elementRef.nativeElement;

            // when click happens on the element we don't need to check for children
            if (hasDifferentTarget) {
              const children: NodeList = (this._elementRef.nativeElement as Element).childNodes;
              children.forEach((node) => {
                if (node === $event.target) {
                  hasDifferentTarget = false;
                }
              });
            }

            return hasDifferentTarget;
          }),
          // only if click didn't happen on the tooltip itself
          filter(($event) => !this.overlayRef.overlayElement.contains($event.target as Node)),
          takeUntil(this.destroyed$),
        )
        .subscribe(() => this.hide());
    } else if (this.trigger === 'hover') {
      listeners.push(
        this.renderer.listen(this._elementRef.nativeElement, 'mouseenter', () => {
          this.show();
        }),
        this.renderer.listen(this._elementRef.nativeElement, 'mouseleave', () => {
          this.hide();
        }),
      );
    }

    this.unregisterListenerFunction = () => listeners.forEach(unregisterFn => unregisterFn());
  }

  show(): void {
    if (this._disabled) {
      return;
    }

    const overlayRef = this._createOverlay();

    this.portal = this.portal || new ComponentPortal<DkTooltipComponent>(DkTooltipComponent, this.viewContainerRef);

    this.instance = overlayRef.attach(this.portal).instance;
    this.instance.content = this.content;
    this.instance.type = this.type;
    this.instance.placement = this.placement;
    this.instance.cssClass = this.tooltipClass;
    this.instance.showArrow = this._showArrow;
    this.isOpen = true;

    this.instance._detectChanges();
    this.changeDetector.markForCheck();

    this.instance.close$.pipe(
      takeUntil(this.destroyed$),
    ).subscribe(() => this.hide());
  }

  /** Create the overlay config and position strategy */
  private _createOverlay(): OverlayRef {
    if (this.overlayRef) {
      return this.overlayRef;
    }

    const scrollableAncestors = this._scrollDispatcher.getAncestorScrollContainers(this._elementRef);

    // Create connected position strategy that listens for scroll events to reposition.
    const strategy = this._overlay.position()
      .flexibleConnectedTo(this._elementRef)
      .withPositions(this.getPreferredPositions())
      .withTransformOriginOn('dk-tooltip')
      .withFlexibleDimensions(false)
      .withViewportMargin(8)
      .withScrollableContainers(scrollableAncestors);

    strategy.positionChanges.pipe(
      takeUntil(this.destroyed$),
    ).subscribe(change => {
      if (this.instance) {
        const newPlacement = this.placementFromPosition(change.connectionPair);

        // NOTE: This is not working
        if (this.instance.placement !== newPlacement) {
          this.instance.placement = newPlacement;
          this.instance._detectChanges();
        }

        if (change.scrollableViewProperties.isOverlayClipped && this.instance.visible) {
          // After position changes occur and the overlay is clipped by
          // a parent scrollable then close the tooltip.
          this.ngZone.run(() => this.hide());
        }
      }
    });

    this.overlayRef = this._overlay.create({
      direction: 'ltr', // this._dir,
      positionStrategy: strategy,
      panelClass: 'dk-tooltip-panel',
    });

    return this.overlayRef;
  }

  hide(): void {
    this.isOpen = false;
    this.overlayRef?.detach();
  }

  private getPreferredPositions(): ConnectedPosition[] {
    return [
      POSITIONS[this.placement],
      getOppositePosition(this.placement),
    ];
  }

  private placementFromPosition(position: ConnectedPosition): Placement {
    for (const [ placement, pos ] of Object.entries(POSITIONS)) {

      if (JSON.stringify(position) === JSON.stringify(pos)) {
        return placement as Placement;
      }
    }

    return 'top';
  }

  ngOnDestroy(): void {
    if (this.unregisterListenerFunction) {
      this.unregisterListenerFunction();
    }
    this.hide();
    this.overlayRef?.dispose();
    this.destroyed$.next();
    this.destroyed$.complete();
  }
}
