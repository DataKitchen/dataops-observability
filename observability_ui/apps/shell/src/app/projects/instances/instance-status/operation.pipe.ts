import { Pipe, PipeTransform } from '@angular/core';
import { DatasetOperationEventData, EventType } from '@observability-ui/core';

@Pipe({
  name: 'operation',
  standalone: true
})

export class OperationPipe implements PipeTransform {
  transform(value: EventType[], operation: 'READ' | 'WRITE'): any {
    if (!value) {
      return;
    }

    return value.filter(x => (x.raw_data as DatasetOperationEventData).operation === operation);
  }
}
