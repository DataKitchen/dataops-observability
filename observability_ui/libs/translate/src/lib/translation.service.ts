import { Injectable } from '@angular/core';
import mustache from 'mustache';

export type Translation = {
  [key: string]: string|Translation;
}

/**
 * Flatten a nested object to an object that has for keys the `join('.')` keys
 * and for values the original values.
 *
 * Caveats all values need to be strings.
 *
 * @param obj
 * @param parent
 */
function* flattenObj(obj: Translation, parent?: string): Generator<{ path: string, value: string }> {

  for (const key in obj) {
    const value = obj[key];
    const path = [ parent, key ].filter((k) => !!k).join('.');

    if (typeof value === 'string') {
      yield { path, value };
    } else {
      yield* flattenObj(value, path);
    }

  }
}

@Injectable({
  providedIn: 'root'
})
export class TranslationService {

  private static translationMap = new Map<string, string>();

  static addTranslations(mappings: Translation[]) {

    mappings.forEach((translationGroup) => {
      const g = [ ...flattenObj(translationGroup) ];

      g.forEach(({ path, value }) => {
        if (TranslationService.translationMap.has(path)) {
          console.warn(`duplicated translation key found "${path}"`);
          const originalValue = TranslationService.translationMap.get(path);
          if (originalValue === value) {
            console.warn('it seems you are registering the same translation more then once');
          } else {
            console.warn(`replacing "${originalValue}" with "${value}"`);

          }
        }

        TranslationService.translationMap.set(path, value);

      });
    });
  }

  translate(key: string, params: object = {}): string {

    if (TranslationService.translationMap.has(key)) {
      return mustache.render(TranslationService.translationMap.get(key) as string, params);
    }

    console.warn(`missing key ${ key }`);
    return key;
  }

}
