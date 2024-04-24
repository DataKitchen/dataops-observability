import { Component, TemplateRef, ChangeDetectorRef, HostBinding } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { Placement } from './dk-tooltip.model';

@Component({
  selector: 'dk-tooltip',
  templateUrl: 'dk-tooltip.component.html',
  styleUrls: [ 'dk-tooltip.component.scss' ],
})
export class DkTooltipComponent {
  visible!: boolean;
  content!: TemplateRef<any> | string;
  type!: 'dropdown' | 'tooltip';
  placement!: Placement;
  showArrow: boolean = true;

  @HostBinding('class') cssClass: string = '';

  private _close$ = new Subject<boolean>();

  constructor(private changeDetector: ChangeDetectorRef) {
  }

  get isTemplateRef(): boolean {
    return this.content instanceof TemplateRef;
  }

  get isDropdown(): boolean {
    return this.type === 'dropdown';
  }

  get close$(): Observable<boolean> {
    return this._close$.asObservable();
  }

  public close(): void {
    this._close$.next(true);
  }

  _markForCheck(): void {
    this.changeDetector.markForCheck();
  }

  _detectChanges(): void {
    this.changeDetector.detectChanges();
  }
}
