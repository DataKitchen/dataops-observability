import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CodeSnippetComponent } from './code-snippet.component';
import { MockModule } from 'ng-mocks';
import { TranslationModule } from '@observability-ui/translate';
import { MatIconModule } from '@angular/material/icon';
import { Clipboard } from '@angular/cdk/clipboard';
import { Mocked } from '@datakitchen/ngx-toolkit';

describe('CodeSnippetComponent', () => {
  let clipboard: Mocked<Clipboard>;

  let fixture: ComponentFixture<CodeSnippetComponent>;
  let component: CodeSnippetComponent;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ MockModule(TranslationModule), MockModule(MatIconModule) ],
      declarations: [ CodeSnippetComponent ],
      providers: [
        {
          provide: Clipboard,
          useClass: class {
            copy = jest.fn();
          }
        }
      ],
    });

    fixture = TestBed.createComponent(CodeSnippetComponent);
    component = fixture.componentInstance;

    clipboard = TestBed.inject(Clipboard) as Mocked<Clipboard>;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('copy()', () => {
    it('should copy a single line to the clipboard', () => {
      component.code = {nativeElement: {innerHTML: 'print("Some python code")'}} as any;

      component.copy();
      expect(clipboard.copy).toBeCalledWith('print("Some python code")');
    });

    it('should copy multiple lines to the clipboard', () => {
      const code = 'def function(param: str) -> None:<br />    print("Do nothing!")';
      component.code = {nativeElement: {innerHTML: code}} as any;

      component.copy();
      expect(clipboard.copy).toBeCalledWith('def function(param: str) -> None:\r\n    print("Do nothing!")');
    });
  });
});
