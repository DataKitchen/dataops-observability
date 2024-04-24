import { AfterViewInit, Component, ContentChildren, EventEmitter, Input, Output, QueryList } from '@angular/core';
import { TypedFormControl } from '@datakitchen/ngx-toolkit';
import { FilterFieldOptionComponent } from './filter-field-option.component';
import { MatLegacyCheckboxChange as MatCheckboxChange } from '@angular/material/legacy-checkbox';
import { AbstractField } from '../abstract-field';
import { BehaviorSubject, combineLatest, debounceTime, map, startWith, takeUntil } from 'rxjs';

@Component({
  selector: 'filter-field',
  templateUrl: 'filter-field.component.html',
  styleUrls: [ 'filter-field.component.scss' ],
})
export class FilterFieldComponent extends AbstractField<FilterFieldOptionComponent[]> implements AfterViewInit {

  @Input() iconOnly!: boolean;
  @Input() label!: string;
  @Input() multiple!: boolean;

  @Input() noneSelectedLabel!: string;
  @Input() allSelectedLabel!: string;

  @Input() searchable!: boolean;
  searchControl = new TypedFormControl<string>();

  @Input() loading: boolean = false;

  @Output() search = new EventEmitter<string>();

  isOpen: boolean = false;

  @ContentChildren(FilterFieldOptionComponent) options!: QueryList<FilterFieldOptionComponent>;

  filteredOptions$: BehaviorSubject<FilterFieldOptionComponent[]> = new BehaviorSubject<FilterFieldOptionComponent[]>([]);

  get indeterminate() {
    return this.selected.length !== this.options.length;
  }

  get selected(): FilterFieldOptionComponent[] {
    return this.options.filter((f) => f.selected);
  }

  override ngAfterViewInit() {
    super.ngAfterViewInit();
    this.options.changes.pipe(
      takeUntil(this.destroyed$)
    ).subscribe((options: FilterFieldOptionComponent[]) => {

      options.forEach((option) => {
        option.selected = this.control.value?.split(',').includes(option.value);
      });
    });

    combineLatest([
      this.searchControl.valueChanges.pipe(
        startWith(''),
      ),
      this.options.changes.pipe(
        startWith(this.options),
      )
    ]).pipe(
      debounceTime(300, this.scheduler),
      map(([ search, options ]) => {
        return options.toArray().filter((f: any) => f.label.match(new RegExp(search ?? '', 'ig')));
      }),
      takeUntil(this.destroyed$),
    ).subscribe((value) => {
      this.filteredOptions$.next(value);
    });
  }

  open() {
    this.isOpen = true;
  }

  close() {
    this.isOpen = false;
  }

  override writeValue(value: string): void {
    this.defer(() => {
      this.clear();

      const values = value?.split(',') || [];
      values.forEach((v) => {
        const o = this.options.find((o) => o.value === v);
        if (o !== undefined) {
          o.selected = true;
        }
      });
    }).after('AfterContentInit');
  }

  select({ checked }: Pick<MatCheckboxChange, 'checked'>, option: FilterFieldOptionComponent) {
    if (!this.multiple) {
      this.options.forEach((o) => o.selected = false);
    }

    option.selected = checked;

    this.commitChanges();

    if (!this.multiple) {
      this.close();
    }
  }

  selectAllChange({ checked }: Pick<MatCheckboxChange, 'checked'>) {
    this.options.forEach((o) => o.selected = checked);

    this.commitChanges();
  }

  commitChanges() {
    this.control?.patchValue(this.selected.map((s) => s.value).join(','));

    // re-emit search filter to allow list of options to be refreshed
    this.searchControl.patchValue(this.searchControl.value);

    this.change.next(this.selected);
  }

  private clear(): void {
    for (const opt of this.options) {
      opt.selected = false;
    }
  }
}
