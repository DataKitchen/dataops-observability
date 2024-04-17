import { NgModule } from '@angular/core';
import { TruncateDirective } from './truncate.directive';

@NgModule({
  declarations: [ TruncateDirective ],
  exports: [ TruncateDirective ]
})
export class TruncateModule {}
