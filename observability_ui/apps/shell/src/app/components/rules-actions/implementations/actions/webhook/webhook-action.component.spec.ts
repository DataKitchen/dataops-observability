import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { WebhookActionComponent } from './webhook-action.component';
import { MockModule } from 'ng-mocks';
import { NgxMonacoEditorModule } from '@datakitchen/ngx-monaco-editor';

describe('webhook-action', () => {

  let component: WebhookActionComponent;
  let fixture: ComponentFixture<WebhookActionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        WebhookActionComponent,
        NoopAnimationsModule,
        MockModule(NgxMonacoEditorModule),
      ],
      declarations: [
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(WebhookActionComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });


  describe('#parse', () => {
    it('should populate the form fields', () => {
      component.parse({
        method: 'POST',
        url: 'https://test',
        payload: {json: "test"},
        headers: [ {key: "hello", value: "world"} ],
      });

      expect(component.form.value).toEqual({
        method: 'POST',
        url: 'https://test',
        payload: '{\n  "json": "test"\n}',
        headers: '[\n  {\n    "key": "hello",\n    "value": "world"\n  }\n]',
      });
    });
  });

  describe('#toJSON', () => {

    it('should parse back to json strings values in payload and headers', () => {

      component.form.patchValue({
        method: 'POST',
        url: 'https://test',
        payload: '{\n  "json": "test"\n}',
        headers: '[\n  {\n    "key": "hello",\n    "value": "world"\n  }\n]',
      });

      const json = component.toJSON();

      expect(json.action_args).toEqual({
        url: 'https://test',
        method: 'POST',
        payload: {
          json: 'test',
        },
        headers: [
          { key: 'hello', value: 'world' }
        ]
      });
    });
  });

});
