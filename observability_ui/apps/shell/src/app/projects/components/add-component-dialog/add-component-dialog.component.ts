import { Component } from '@angular/core';
import { Validators } from '@angular/forms';
import { BaseComponent, ComponentType, CustomValidators, nonReadonlyFields, ProjectStore } from '@observability-ui/core';
import { TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { filter, map, shareReplay, switchMap } from 'rxjs';
import { ComponentStore } from '../components.store';
import { ComponentsService } from '../../../services/components/components.service';
import { takeUntilDestroyed, toSignal } from '@angular/core/rxjs-interop';
import { MatLegacyDialogRef } from '@angular/material/legacy-dialog';

@Component({
  selector: 'shell-add-component-dialog',
  templateUrl: './add-component-dialog.component.html',
  styleUrls: [ './add-component-dialog.component.scss' ]
})
export class AddComponentDialogComponent {

  private projectId = toSignal(this.projectStore.current$.pipe(map(({ id }) => id)));

  adding$ = this.store.getLoadingFor('create');

  addAction$ = this.store.loading$.pipe(
    filter(({ code }) => code === 'create'),
    filter(({ status }) => status === false),
  );

  componentKeys$ = this.projectStore.current$.pipe(
    switchMap(project => this.service.findAll({parentId: project.id})),
    map(({entities}) => entities.map(component => component.key)),
    shareReplay(1),
  );

  formGroup = new TypedFormGroup <nonReadonlyFields<BaseComponent>> ({
    type: new TypedFormControl<ComponentType>(
      null,
      [Validators.required]
    ),
    key: new TypedFormControl<string>(
      null,
      [Validators.required, Validators.maxLength(255)],
      [CustomValidators.forbiddenNamesAsync(this.componentKeys$)]
    ),
    name: new TypedFormControl<string>(null, [Validators.required]),
    description: new TypedFormControl<string>(null),
    tool: new TypedFormControl<string>(undefined),
  });

  error: any;
  ComponentType = ComponentType;
  componentTypes = Object.values(ComponentType).sort();


  constructor(
    private dialog: MatLegacyDialogRef<any>,
    private store: ComponentStore,
    private service: ComponentsService,
    private projectStore: ProjectStore,
  ) {

    this.addAction$.pipe(
      takeUntilDestroyed()
    ).subscribe((event) => {
      if (event.error) {
        this.error = event.error?.error?.error;
        /**
         * Example event.error 👇
         *
         * { "headers": { "normalizedNames": {}, "lazyUpdate": null }, "status": 400, "statusText": "OK", "url": "https://<domain>/observability/v1/projects/6238a101-74e0-4edb-93c6-994da8fa2c2d/batch-pipelines", "ok": false, "name": "HttpErrorResponse", "message": "Http failure response for https://<domain>/observability/v1/projects/6238a101-74e0-4edb-93c6-994da8fa2c2d/batch-pipelines: 400 OK", "error": { "details": {}, "error": "{'tool': ['Unknown field.']}" } }
         */
      } else {
        this.dialog.close();
      }
    });
  }

  addComponent(form: nonReadonlyFields<BaseComponent>): void {
    this.store.dispatch('create', form, this.projectId());
  }
}
