import { NgModule } from '@angular/core';
import { DynamicComponentOutletDirective } from './dynamic-component-outlet.directive';

@NgModule({
  imports: [],
  exports: [
    DynamicComponentOutletDirective,
  ],
  declarations: [
    DynamicComponentOutletDirective,
  ],
  providers: [],
})
export class DynamicComponentModule {
}
