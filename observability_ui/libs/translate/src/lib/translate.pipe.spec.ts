import { TranslationService } from './translation.service';
import { TranslatePipe } from './translate.pipe';
import { TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';

describe('Translate Pipe', () => {

  const key = 'createKitchen.summary';
  const key2 = 'invalid.key';
  const params = {kitchen: 'kitchenA'};
  const translatedValue = 'translated value';
  const translatedValueParams = 'translated value with params';

  let translationService: TranslationService;
  let translatePipe: TranslatePipe;

  beforeEach(() => {
    TestBed.configureTestingModule({

      providers: [
        MockProvider(TranslationService, {
          translate: jest.fn().mockImplementation( (key, params) => {
            if (key === key2) {
              return key2;
            }

            return params ? translatedValueParams : translatedValue;
          })
        }),
        TranslatePipe,
      ]
    });


    translatePipe = TestBed.inject(TranslatePipe);
    translationService = TestBed.inject(TranslationService);
  });

  it('should return translated value for specified key', () => {
    const value = translatePipe.transform(key);
    expect(value).toBe(translatedValue);
    expect(translationService.translate).toHaveBeenCalledWith(key, undefined);
  });

  it('should return translated value for specified key and parameters', () => {
    const value = translatePipe.transform(key, params);
    expect(value).toBe(translatedValueParams);
    expect(translationService.translate).toHaveBeenCalledWith(key, params);
  });

  it('should return the provided default if the specified key is missing', () => {
    const value = translatePipe.transform(key2, {}, 'Default');
    expect(value).toBe('Default');
  });
});
