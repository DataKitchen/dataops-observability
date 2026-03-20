import { BaseComponent, ComponentType, JourneyInstanceRule, ProjectStore } from '@observability-ui/core';
import { CoreComponent, TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { Component, OnInit } from '@angular/core';
import { Validators } from '@angular/forms';
import { MatLegacyDialogRef as MatDialogRef } from '@angular/material/legacy-dialog';
import { JourneysStore } from '../journeys.store';
import { filter, map, merge, Observable, takeUntil } from 'rxjs';
import { ActivatedRoute, Router } from '@angular/router';
import { ComponentsService } from '../../../services/components/components.service';
import { JourneysService } from '../../../services/journeys/journeys.service';
import { tap } from 'rxjs/operators';

@Component({
  selector: 'shell-add-journey-dialog',
  templateUrl: './add-journey-dialog.component.html',
  styleUrls: [ './add-journey-dialog.component.scss' ]
})
export class AddJourneyDialogComponent extends CoreComponent implements OnInit {
  private projectId: string;

  adding$ = this.store.getLoadingFor('createOne');
  components$: Observable<BaseComponent[]>;

  previewResults: Pick<BaseComponent, 'key' | 'name'>[] | null = null;
  previewing = false;

  error: any;

  addAction$ = this.store.loading$.pipe(
    filter(({code}) => code === 'createOne'),
    filter(({status}) => status === false),
  );

  formGroup = new TypedFormGroup<{ name: string, description: string, component_include_patterns: string, component_exclude_patterns: string, instance_rules: JourneyInstanceRule[] }>(({
    name: new TypedFormControl<string>(null, [ Validators.required ]),
    description: new TypedFormControl<string>(null),
    component_include_patterns: new TypedFormControl<string>(null),
    component_exclude_patterns: new TypedFormControl<string>(null),
    instance_rules: new TypedFormControl<JourneyInstanceRule[]>([]),
  }));

  constructor(
    private dialog: MatDialogRef<any>,
    private store: JourneysStore,
    private router: Router,
    private route: ActivatedRoute,
    private service: JourneysService,
    protected componentsService: ComponentsService,
    private projectStore: ProjectStore,
  ) {
    super();
  }

  override ngOnInit() {
    super.ngOnInit();

    this.projectStore.current$.pipe(
      takeUntil(this.destroyed$)
    ).subscribe((project) => {
      this.projectId = project.id;
      this.components$ = this.componentsService.findAll({ parentId: this.projectId, filters: { component_type: [ ComponentType.BatchPipeline ] } }).pipe(
        map(response => response.entities),
      );
    });

    merge(
      this.formGroup.controls.component_include_patterns.valueChanges,
      this.formGroup.controls.component_exclude_patterns.valueChanges,
    ).pipe(takeUntil(this.destroyed$)).subscribe(() => this.previewResults = null);

    this.addAction$.pipe(
      takeUntil(this.destroyed$),
      tap(({ error }) => {
        if (error) {
          this.error = error;
        }
      }),
      map(({ response }) => response.id)
    ).subscribe((journeyId?: string) => {

      if (journeyId) {
        this.dialog.close();
        void this.router.navigate([ journeyId ], { relativeTo: this.route });
      }
    });
  }

  previewComponents(): void {
    this.previewing = true;
    this.service.previewComponentPatterns(
      this.projectId,
      this.formGroup.value.component_include_patterns,
      this.formGroup.value.component_exclude_patterns,
    ).pipe(takeUntil(this.destroyed$)).subscribe({
      next: (components) => {
        this.previewResults = components;
        this.previewing = false;
      },
      error: () => {
        this.previewing = false;
      },
    });
  }

  addJourney({ name, description, component_include_patterns, component_exclude_patterns, instance_rules }: { name: string, description: string, component_include_patterns: string, component_exclude_patterns: string, instance_rules: JourneyInstanceRule[] }) {
    this.store.dispatch('createOne', { name, description, component_include_patterns, component_exclude_patterns, instance_rules, project_id: this.projectId });
  }
}
