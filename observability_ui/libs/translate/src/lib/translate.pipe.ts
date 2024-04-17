import { Pipe, PipeTransform } from '@angular/core';
import { TranslationService } from './translation.service';

@Pipe({
  name: 'translate',
})
export class TranslatePipe implements PipeTransform {
  constructor(private translationService: TranslationService) {
  }

  public transform(key: string, params?: object, defaultTo?: string): string {
    const translation = this.translationService.translate(key, params);
    if (translation === key && defaultTo) {
      return defaultTo;
    }
    return translation;
  }
}
