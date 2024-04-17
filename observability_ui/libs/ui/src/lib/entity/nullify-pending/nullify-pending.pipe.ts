import { Pipe, PipeTransform } from '@angular/core';

@Pipe({name: 'nullifyPending'})
export class NullifyPendingPipe implements PipeTransform {

  transform<T>(value: T) {
    if (typeof value === 'string') {
      return value.startsWith('_DK_PENDING_') ? null : value;
    }
    return value;
  }
}
