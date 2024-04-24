import { Component, computed, inject } from '@angular/core';
import { CoreComponent } from '@datakitchen/ngx-toolkit';
import { map, startWith } from 'rxjs';
import { FormControl } from '@angular/forms';
import { INTEGRATION_TOOLS } from '../integrations.model';
import { toSignal } from '@angular/core/rxjs-interop';

@Component({
  selector: 'shell-integrations-panel',
  templateUrl: 'integrations-panel.component.html',
  styleUrls: [ 'integrations-panel.component.scss' ],
})

export class IntegrationsPanelComponent extends CoreComponent {
  searchControl = new FormControl();
  integrations = computed(() => this.tools.filter((tool) => tool._displayName.toLowerCase().includes(this.searchValue() ?? '')));

  private searchValue = toSignal(
    this.searchControl.valueChanges.pipe(
      startWith(''),
      map((term: string) => term?.trim()?.toLowerCase() ?? ''),
    )
  );
  private tools = inject(INTEGRATION_TOOLS);
}
