import {ProjectAlertSettingsStore} from "./project-alerts.store";
import {TestBed} from "@angular/core/testing";
import {ProjectService} from "@observability-ui/core";
import {MockProvider} from "@datakitchen/ngx-toolkit";

describe('ProjectAlertSettingsStore', () => {
  let store: ProjectAlertSettingsStore;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        ProjectAlertSettingsStore,
        MockProvider(ProjectService),
      ]
    });

    store = TestBed.inject(ProjectAlertSettingsStore);

  });

  it('should create', () => {
    expect(store).toBeTruthy();
  });

});
