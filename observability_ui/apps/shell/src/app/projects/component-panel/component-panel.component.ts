import { Component, effect } from '@angular/core';
import { BaseComponent, ComponentType, nonReadonlyFields, ProjectStore, Schedule} from '@observability-ui/core';
import { TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { AbstractControl, Validators } from '@angular/forms';
import { BehaviorSubject, filter, map, Observable, startWith, take, tap } from 'rxjs';
import { ActivatedRoute, Router } from '@angular/router';
import { ComponentStore, ComponentUI } from '../components/components.store';
import { JourneysStore } from '../journeys/journeys.store';
import { MatLegacyDialog as MatDialog } from '@angular/material/legacy-dialog';
import { DeleteComponentDialogComponent } from './delete-component-dialog/delete-component-dialog.component';
import { takeUntilDestroyed, toSignal } from '@angular/core/rxjs-interop';
import { DagStore } from '../../stores/dag/dag.store';


@Component({
  selector: 'shell-component-panel',
  templateUrl: 'component-panel.component.html',
  styleUrls: [ 'component.panel.component.scss' ],
})
export class ComponentPanelComponent {


  loading$ = this.componentsStore.getLoadingFor('getOne').pipe(
    startWith(true),
  );

  component$: Observable<ComponentUI> = this.componentsStore.selected$.pipe(
    tap((component) => {

      this.component = component;

      this.form.patchValue({
        // this also patches `expectedArrivalWindow`
        ...component,
        name: component.name ?? '',
        description: component.description ?? '',
      });

    }),
  );

  component: ComponentUI;

  saving$ = this.componentsStore.getLoadingFor('updateOne');

  error$ = this.componentsStore.loading$.pipe( // TODO: we should try accumulating errors into an array for subsequent errors, then reset when error === null
    filter(({ code }) => code === 'updateOne'),
    filter(({ status }) => status === false),
    map(({ error }) => error ? ((error as Error)?.message ?? String(error)) : null),
  );

  projectId$ = this.projectStore.current$.pipe(
    map(project => project.id),
  );

  componentJourneys$ = this.journeysStore.list$;

  editing$ = new BehaviorSubject(false);

  form = new TypedFormGroup<nonReadonlyFields<ComponentUI> & {
    expectedArrivalWindow: Schedule;
    startsAt: Schedule,
    endsAt: Schedule,
  }>({
    id: new TypedFormControl<string>(null, Validators.required),
    name: new TypedFormControl<string>(''),
    key: new TypedFormControl<string>(null, Validators.required),
    type: new TypedFormControl<ComponentType>(null, Validators.required),
    description: new TypedFormControl<string>('', Validators.maxLength(255)),
    tool: new TypedFormControl<string>(undefined),

    expectedArrivalWindow: new TypedFormControl<Schedule>(undefined, [ this.validateExpectedArrivalWindow.bind(this) ]),

    startsAt: new TypedFormControl<Schedule>(undefined, [ this.validateStartsAt.bind(this) ]),
    endsAt: new TypedFormControl<Schedule>(),
  }, []);

  componentType = ComponentType;

  constructor(
    private route: ActivatedRoute,
    private componentsStore: ComponentStore,
    private dagStore: DagStore,
    private router: Router,
    private projectStore: ProjectStore,
    private journeysStore: JourneysStore,
    private dialog: MatDialog
  ) {

    const deleted = toSignal(this.componentsStore.loading$.pipe(
      filter(({ code }) => code === 'deleteComponent'),
      filter(({ error }) => !error),
    ));

    // redirect after deletion
    effect(() => {
      if (deleted()?.response) {
        void this.router.navigate([ '..' ], { relativeTo: this.route });
      }
    });

    this.componentsStore.loading$.pipe(
      filter(({ code }) => code === 'updateOne'),
      filter(({ status }) => status === false),
      filter(({ error }) => !error),
      takeUntilDestroyed(),
    ).subscribe(() => this.setEditing(false));

    this.componentsStore.dispatch('getOne', this.route.snapshot.params['id']);

    // Get related journeys
    this.projectId$.pipe(
      take(1),
      tap(projectId => {
        this.journeysStore.dispatch('findAll', {
          parentId: projectId,
          filters: { component_id: this.route.snapshot.params['id'] }
        });
      })
    ).subscribe();

  }

  setEditing(editing: boolean): void {
    this.editing$.next(editing);
  }


  save() {
    const { expectedArrivalWindow, startsAt, endsAt, ...component } = this.form.value;

    this.componentsStore.dispatch('updateOne', {
      ...component,
      display_name: component.name,
    } as unknown as ComponentUI, {
      expectedArrivalWindow,
      startsAt,
      endsAt,
    });

    this.dagStore.dispatch('updateNodeInfo', {
      ...component,
      display_name: component.name,
    } as BaseComponent);

  }

  openDeleteComponent(component: BaseComponent) {
    this.dialog.open(DeleteComponentDialogComponent, {
      width: '500px',
      data: component
    }).afterClosed().pipe(
      tap((id: string) => {
        if (id) {
          this.componentsStore.dispatch('deleteComponent', id);
        }
      }),
    ).subscribe();
  }


  // TODO below functions are duplicating code because we'd need to check the `expectation` field
  // in order to do both validations in the same function.
  // We can achieve that easier after migrating how form-driven-components to MatFormFieldControl components
  private validateExpectedArrivalWindow(fc: AbstractControl<Schedule>): { [key: string]: boolean } | null {

    if (!this.form) {
      return null;
    }

    const { margin, schedule } = fc.value || {};

    // reset errors
    this.form.setErrors(null);

    let error = null;

    if (margin && !schedule) {
      // missing schedule
      error = { schedule: true };
    }

    if (!margin && schedule) {
      error = { margin: true };
    }

    if (schedule && margin < 300) {
      error = { min_margin: true };
    }

    this.form.setErrors(error);

    return error;
  }

  private validateStartsAt(fc: AbstractControl<Schedule>): { [key: string]: boolean } | null {

    if (!this.form) {
      return null;
    }

    const { margin, schedule } = fc.value || {};

    // reset errors
    this.form.setErrors(null);

    let error = null;

    if (margin && !schedule) {
      // missing schedule
      error = { schedule: true };
    }

    if (!margin && schedule) {
      error = { margin: true };
    }

    this.form.setErrors(error);

    return error;
  }
}
