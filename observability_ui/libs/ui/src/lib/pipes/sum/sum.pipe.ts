import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'sum',
  standalone: true,
})
export class SumPipe implements PipeTransform {
  transform(items: Array<any>, key?: string) {
    return items.reduce((total, item) => total + this.getValue(item, key), 0);
  }

  private getValue(item: any, key?: string): number {
    if (!key) {
      return item;
    }

    let result = item;
    const parts = key?.trim().split(".");
    for (const part of parts) {
      result = item[part];
    }

    return result ?? 0;
  }
}
