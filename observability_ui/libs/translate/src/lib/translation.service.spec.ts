import { TranslationService } from './translation.service';
import { NgModule } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { TranslationModule } from './translation.module';
import spyOn = jest.spyOn;


describe('Translation Service', () => {
  spyOn(console, 'warn').mockImplementation();


  const rootTranslations = {
    mainTitle: 'Main Fruit',
    mainActions: {
      eat: 'Eat',
      name: 'This fruit is called {{name}}',
    },
    bear: 'bear',
  };
  const childTranslations = {
    moduleTitle: 'Module Fruit',
    moduleActions: {
      peel: 'Peel',
    },
    user: 'user',
  };

  const dups = {
    moduleTitle: 'Module Veggies'
  };

  let translationService: TranslationService;

  @NgModule({
    imports: [
      TranslationModule.forChild(childTranslations, dups, dups),
    ],
  })
  class ChildModule {
  }

  @NgModule({
    imports: [
      ChildModule,
      TranslationModule.forRoot(rootTranslations),
    ],
  })
  class AppModule {
  }

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        AppModule,
      ],
    }).compileComponents();

    translationService = TestBed.inject(TranslationService);


  });

  it('should create', () => {
    expect(translationService).toBeTruthy();
  });

  it('should translate key, if it exists in any registered mapping', () => {
    expect(translationService.translate('mainTitle')).toBe('Main Fruit');
    expect(translationService.translate('moduleTitle')).toBe('Module Veggies');
  });

  it('should translate nested key, if it exists in any registered mapping', () => {
    expect(translationService.translate('mainActions.eat')).toBe('Eat');
    expect(translationService.translate('moduleActions.peel')).toBe('Peel');
  });

  it('should return key, if it does not exist in any registered mappings', () => {
    expect(translationService.translate('fruit.stuff')).toBe('fruit.stuff');
  });

  it('should translate key with parameters: interpolation', () => {
    expect(translationService.translate('mainActions.name', {name: 'Bob'})).toBe('This fruit is called Bob');
  });

  it('should translate entity key, if it exists in the entity mapping', () => {
    expect(translationService.translate('user')).toBe('user');
  });
});
