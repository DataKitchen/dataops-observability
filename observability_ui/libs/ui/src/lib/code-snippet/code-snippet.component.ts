import { Component, ElementRef, ViewChild } from '@angular/core';
import { Clipboard } from '@angular/cdk/clipboard';
import { MatIconModule } from '@angular/material/icon';
import { TranslationModule } from '@observability-ui/translate';
import { TruncateModule } from '../truncate';

@Component({
  selector: 'code-snippet',
  templateUrl: 'code-snippet.component.html',
  styleUrls: [ 'code-snippet.component.scss' ],
  standalone: true,
  imports: [
    MatIconModule,
    TranslationModule,
    TruncateModule
  ]
})
export class CodeSnippetComponent {
  @ViewChild('code') code!: ElementRef<HTMLElement>;
  copied = false;

  constructor(public clipboard: Clipboard) {
  }

  copy() {
    this.clipboard.copy(this.getSnippet());

    this.copied = true;

    setTimeout(() => {
      this.copied = false;
    }, 2000);
  }

  // TODO: Create a code-snippet-line for better multi-line support (?)
  private getSnippet(): string {
    return this.code.nativeElement.innerHTML
      .split(/<br.*[/]?>/gi)
      .map(line => this.decodeHTML(line))
      .join('\r\n')
      .trim();
  }

  private decodeHTML(text: string): string {
    const textarea = document.createElement('textarea');
    textarea.innerHTML = text;
    return textarea.textContent ?? '';
  }
}
