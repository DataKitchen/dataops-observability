import { ModuleWithProviders, NgModule } from '@angular/core';
import { Translation, TranslationService } from './translation.service';
import { TranslatePipe } from './translate.pipe';

@NgModule({
  imports: [],
  exports: [ TranslatePipe ],
  declarations: [ TranslatePipe ],
})
export class TranslationModule {

  // Meant to be imported once in the main module, so only single instance of the service is created
  static forRoot(...mappings: Translation[]): ModuleWithProviders<TranslationModule> {
    TranslationService.addTranslations(mappings);
    return {
      ngModule: TranslationModule,
      providers: [
        TranslationService,
      ],
    };
  }

  // Meant to be imported in feature/lazy-loaded modules to register mappings for each module
  static forChild(...mappings: Translation[]): ModuleWithProviders<TranslationModule> {
    TranslationService.addTranslations(mappings);
    return {
      ngModule: TranslationModule,
    };
  }
}
