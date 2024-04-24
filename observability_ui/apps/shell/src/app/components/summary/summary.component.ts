import { AfterContentInit, Component, ContentChildren, QueryList } from '@angular/core';
import { SummaryItemComponent } from '../summary-item/summary-item.component';
import { CoreComponent } from '@datakitchen/ngx-toolkit';
import { startWith, takeUntil } from 'rxjs';

@Component({
  selector: 'shell-summary',
  templateUrl: 'summary.component.html',
  styleUrls: [ 'summary.component.scss' ],
  imports: [
    SummaryItemComponent,
  ],
  standalone: true
})

export class SummaryComponent extends CoreComponent implements AfterContentInit {
  @ContentChildren(SummaryItemComponent) items: QueryList<SummaryItemComponent>;

  total: number = 0;

  override ngAfterContentInit() {
    super.ngAfterContentInit();
    this.items.changes.pipe(
      startWith(this.items),
      takeUntil(this.destroyed$),
    ).subscribe((value) => {
      if (value) {
        this.total = this.items.reduce((acc, item) => parseInt(acc.toString()) + parseInt(item.count?.toString(0)) ?? 0, 0);
      }
    });
  }
}
