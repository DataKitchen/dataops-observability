import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'duration',
  template: `{{ (start|date:dateFormat)|duration:(end|date:dateFormat)}}`
})
export class DurationComponent implements OnInit {

  @Input() start!: string;
  @Input() end!: string;

  dateFormat = 'EEEE, MMMM d, y, h:mm:ss a zzzz';

  ngOnInit() {
    if (!this.end) {
      this.end = new Date().getTime().toString();
    }
  }

}
