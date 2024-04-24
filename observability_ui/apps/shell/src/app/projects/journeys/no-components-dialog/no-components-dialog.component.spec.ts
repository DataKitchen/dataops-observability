import { NoComponentsDialogComponent } from './no-components-dialog.component';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { ActivatedRoute } from '@angular/router';

fdescribe('no-components-dialog', () => {
  let fixture: ComponentFixture<NoComponentsDialogComponent>;

  beforeEach(async () => {

    await TestBed.configureTestingModule({
      imports: [
        NoComponentsDialogComponent,
      ],
      providers: [
        MockProvider(ActivatedRoute)
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(NoComponentsDialogComponent);
  });

  it('should create', () => {
    expect(fixture.componentInstance).toBeTruthy();
  });
});
