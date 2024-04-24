import { Component, effect, ViewChild, ViewContainerRef } from '@angular/core';
import { ProjectStore, ServiceKey, } from '@observability-ui/core';
import { BindToQueryParams, CoreComponent, HasPaginator, HasSearchForm, ParameterService, PersistOnLocalStorage, Prop, StorageService, TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { toSignal } from '@angular/core/rxjs-interop';
import { DatePipe, NgIf } from '@angular/common';
import { APIKeysStore } from './api-keys.store';
import { ConfirmDialogComponent, HelpLinkComponent, SelectedActionsComponent, EmptyStateSetupComponent, TableChangeEvent, TableWrapperComponent, TableWrapperModule, TextFieldModule, TruncateModule } from '@observability-ui/ui';
import { FlexModule } from '@angular/flex-layout';
import { TranslationModule } from '@observability-ui/translate';
import { RouterLink } from '@angular/router';
import { debounceTime, map, Subject } from 'rxjs';
import { MatIconModule } from '@angular/material/icon';
import { MatLegacyDialog as MatDialog, MatLegacyDialogModule as MatDialogModule } from '@angular/material/legacy-dialog';
import { MatLegacyButtonModule } from '@angular/material/legacy-button';
import { AddApiKeyModalComponent } from './add-api-key-modal/add-api-key-modal.component';
import { MatLegacyMenuModule } from '@angular/material/legacy-menu';
import { DeleteKeyModalComponent } from './delete-keys-modal/delete-key-modal.component';
import { ReactiveFormsModule } from '@angular/forms';
import { MatPaginator } from '@angular/material/paginator';


@Component({
  selector: 'shell-api-keys',
  templateUrl: './api-keys.component.html',
  standalone: true,
  imports: [ NgIf, TableWrapperModule, FlexModule, TranslationModule, RouterLink, TruncateModule, MatIconModule, MatDialogModule, MatLegacyButtonModule, DatePipe, SelectedActionsComponent, MatLegacyMenuModule, TextFieldModule, ReactiveFormsModule, EmptyStateSetupComponent, HelpLinkComponent ],
  styleUrls: [ 'api-keys.component.scss' ]
})
export class APIKeysComponent extends CoreComponent implements HasPaginator, HasSearchForm<any> {
  @ViewChild(TableWrapperComponent) table: TableWrapperComponent;
  @ViewChild(MatPaginator) paginator!: MatPaginator;
  search$: Subject<any> = new Subject<any>();

  pageChange = toSignal(this.__pageChange$);
  searchSignal = toSignal(this.search$);

  currentProject = toSignal(this.projectStore.current$);
  apiKeys = toSignal(this.apiKeysStore.list$.pipe(
    map((keys) =>
      keys.map((key) => ({
        ...key,
        expired: new Date(key.expires_at) <= new Date(),
        expiring_soon: new Date(key.expires_at) > new Date() && new Date(key.expires_at) <= new Date(new Date().setDate(new Date().getDate() + 7)), // 7 days
        send_events_allowed: key.allowed_services?.includes('EVENTS_API'),
        manage_entities_allowed: key.allowed_services?.includes('OBSERVABILITY_API'),
        send_heartbeat_allowed: key.allowed_services?.includes('AGENT_API'),
      }))
    ),
  ));
  total = toSignal(this.apiKeysStore.total$);

  loading = toSignal(this.apiKeysStore.getLoadingFor('getPage'));
  createLoading = toSignal(this.apiKeysStore.getLoadingFor('create'));

  @BindToQueryParams()
  @PersistOnLocalStorage({ namespace: Prop('storageKey') })
  search = new TypedFormGroup<{ search: string }>({
    search: new TypedFormControl('')
  });

  searchChange = toSignal(this.search.valueChanges.pipe(
    debounceTime(300)
  ));

  filtersApplied = toSignal(this.search$.pipe(
    map(({ search }) => !!search),
  ));

  constructor(
    private projectStore: ProjectStore,
    private apiKeysStore: APIKeysStore,
    private dialog: MatDialog,
    private viewContainerRef: ViewContainerRef,
    protected paramService: ParameterService,
    protected override storageService: StorageService,
  ) {
    super(paramService, storageService);

    effect(() => {
      const parentId = this.currentProject()?.id;
      const { pageIndex: page, pageSize: count } = this.pageChange() || {};
      const filters = this.searchSignal();

      this.apiKeysStore.dispatch('getPage', {
        parentId,
        page,
        count,
        filters
      });
    }, { allowSignalWrites: true });
  }

  onTableChange({ pageIndex, pageSize }: TableChangeEvent) {
    this.__pageChange$.next({ pageIndex, pageSize, length: undefined });
  }

  confirmDelete(apiKey: ServiceKey) {
    this.dialog.open(ConfirmDialogComponent, {
      data: {
        title: 'Delete API key',
        message: `Are you sure you want to delete API key ${apiKey.name}`,
        confirmLabel: 'Delete',
        confirmButtonColor: 'warn',
        id: apiKey.id
      },
    }).afterClosed().subscribe(({ id }) => {
      if (id) {
        this.apiKeysStore.dispatch('deleteOne', id);
      }
    });
  }

  openAddAPIKey() {
    this.dialog.open(AddApiKeyModalComponent, {
      width: '500px',
      autoFocus: false,
      viewContainerRef: this.viewContainerRef
    }).afterClosed().subscribe(() => {
      this.apiKeysStore.dispatch('clearToken');
    });
  }

  deleteSelected() {
    this.dialog.open(DeleteKeyModalComponent, {
      width: '600px',
      data: {
        ids: this.table.selection.selected,
      }
    }).afterClosed().subscribe(() => {
      this.table.selection.clear();
    });
  }
}
