import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ToolDisplayComponent } from './tool-display.component';
import { MockModule, MockProvider } from 'ng-mocks';
import { ActivatedRoute } from '@angular/router';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ConfigService } from '@observability-ui/core';
import { of } from 'rxjs';
import { MatIconModule } from '@angular/material/icon';

describe('ToolDisplayComponent', () => {
  let component: ToolDisplayComponent;
  let fixture: ComponentFixture<ToolDisplayComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ ToolDisplayComponent ],
      imports: [
        HttpClientTestingModule,
        MockModule(MatIconModule)
      ],
      providers: [
        MockProvider(ActivatedRoute, {
          parent: {
            parent: 'id'
          },
          params: of({})
        } as any),
        MockProvider(ConfigService)
      ]
    });
    fixture = TestBed.createComponent(ToolDisplayComponent);
    component = fixture.componentInstance;
  });

  it('should create the component', () => {
    expect(component).toBeTruthy();
  });
});
