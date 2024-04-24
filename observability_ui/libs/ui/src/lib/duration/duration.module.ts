import { NgModule } from '@angular/core';
import { DurationPipe } from './duration.pipe';
import { DurationComponent } from './duration.component';
import { CommonModule } from '@angular/common';

@NgModule({
  imports: [ CommonModule ],
  declarations: [ DurationPipe, DurationComponent ],
  exports: [ DurationPipe, DurationComponent ]
})
export class DurationModule {}
