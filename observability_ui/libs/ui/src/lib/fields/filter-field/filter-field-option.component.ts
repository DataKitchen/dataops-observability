import { AfterViewInit, Component, ElementRef, Input, ViewChild } from '@angular/core';

@Component({
  selector: 'filter-field-option',
  template: `
      <div #content>
        <ng-content></ng-content>
      </div>
  `
})
export class FilterFieldOptionComponent implements AfterViewInit {

  @ViewChild('content', {read: ElementRef, static: true}) content!: ElementRef;

  hasContent = false;
  html!: string;

  @Input() value!: string | number | boolean;
  @Input() disabled!: boolean;
  @Input() label!: string;
  @Input() selected!: boolean;

  ngAfterViewInit() {
    this.hasContent = this.content.nativeElement.innerHTML !== '';
    this.html = this.content.nativeElement.innerHTML;

    if (!this.label) {
      if (!this.hasContent) {

        throw new Error(`FilterFieldOptionComponent with value ${this.value} must have at least a label or some content`);
      } else {
        this.label = this.content.nativeElement.textContent.trim();
      }
    }

  }
}
