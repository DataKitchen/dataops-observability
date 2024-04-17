import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'humanize',
  pure: true,
  standalone: true,
})
export class HumanizePipe implements PipeTransform {
  transform(value: string): string {
    if (!value) {
      return '';
    }
    return this.humanize(value);
  }

  private humanize(slug: string): string {
    return slug.replace(/[_-]/g, ' ');
  }
}
