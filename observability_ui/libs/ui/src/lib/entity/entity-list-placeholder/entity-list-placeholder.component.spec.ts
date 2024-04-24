import { ComponentFixture, TestBed } from '@angular/core/testing';
import { EntityListPlaceholderComponent } from './entity-list-placeholder.component';
import { By } from '@angular/platform-browser';
import { TranslatePipeMock } from '@observability-ui/translate';
import { MockComponent } from '@datakitchen/ngx-toolkit';

describe('Entity List Placeholder Component', () => {

  let fixture: ComponentFixture<EntityListPlaceholderComponent>;
  let component: EntityListPlaceholderComponent;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [
        EntityListPlaceholderComponent,
        TranslatePipeMock,
        MockComponent({
          selector: 'mat-spinner',
        }),
      ],
    });

    fixture = TestBed.createComponent(EntityListPlaceholderComponent);
    component = fixture.componentInstance;
  });

  it('should exist', () => {
    expect(component).toBeDefined();
  });

  it('should not display, if not loading and total is non-zero', () => {
    component.loading = false;
    component.total = 10;
    fixture.detectChanges();
    const divElement = fixture.debugElement.query(By.css('div'));
    expect(divElement).toBeNull();
  });

  it('should display only spinner, if loading is true', () => {
    component.loading = true;
    component.total = 10;
    fixture.detectChanges();

    const spinnerElement = fixture.debugElement.query(By.css('mat-spinner'));
    expect(spinnerElement).not.toBeNull();

    const {textContent} = fixture.nativeElement as HTMLElement;
    expect(textContent).not.toContain('noEntitiesForFilters');
    expect(textContent).not.toContain('noEntitiesFound');
  });

  it('should display text only, if loading is false and total is zero: no filters', () => {
    component.loading = false;
    component.total = 0;
    component.hasFilters = false;
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('noEntitiesFound');

    const spinnerElement = fixture.debugElement.query(By.css('mat-spinner'));
    expect(spinnerElement).toBeNull();
  });

  it('should display text only, if loading is false and total is zero: has filters', () => {
    component.loading = false;
    component.total = 0;
    component.hasFilters = true;
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('noEntitiesForFilters');

    const spinnerElement = fixture.debugElement.query(By.css('mat-spinner'));
    expect(spinnerElement).toBeNull();
  });
});
