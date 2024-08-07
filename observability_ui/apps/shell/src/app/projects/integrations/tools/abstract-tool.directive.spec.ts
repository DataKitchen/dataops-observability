import { Component } from '@angular/core';
import { AbstractTool } from './abstract-tool.directive';
import { FormControl, FormGroup } from '@angular/forms';
import { TestBed } from '@angular/core/testing';
import { ConfigService, ProjectService, ProjectStore } from '@observability-ui/core';
import { MockProvider, Mocked } from '@datakitchen/ngx-toolkit';
import { of } from 'rxjs';

jest.mock('./agent-script.tpl', () => ({
  default: `
  EVENTS_API_HOST="{{events_api_host}}"
  EVENTS_API_KEY="{{events_api_key}}"
  EVENT_HUB_CONN_STR="{{event_hub_conn_str}}"
  EVENT_HUB_NAME="{{event_hub_name}}"
  AZURE_STORAGE_CONN_STR="{{azure_storage_conn_str}}"
  BLOB_CONTAINER_NAME="{{blob_container_name}}"
  EXTERNAL_PLUGINS_PATH="{{external_plugins_path}}"
  ENABLED_PLUGINS="{{enabled_plugins}}"
  PUBLISH_EVENTS="{{publish_events}}"
  AIRFLOW_PASSWORD="{{airflow_password}}"
  AIRFLOW_USERNAME="{{airflow_username}}"
  BASE_AIRFLOW_API_URL="{{base_airflow_api_url}}"
  DOCKER_IMAGE="{{docker_image}}"
  DOCKER_TAG="{{docker_tag}}"
  DOCKER_EXTRA_ENV_VARS="{{docker_extra_env_vars}}"
  KUBERNETES_EXTRA_ENV_VARS="{{kubernetes_extra_env_vars}}"
  DEFAULT_DEPLOYMENT_MODE="{{default_deployment_mode}}"
  TARGET_SERVICE="{{target_service}}"
  `,
}));

jest.mock('./agent-script-v2.tpl', () => ({
  default: `
  DK_AGENT_TYPE='{{agent_type}}'
  DK_AGENT_KEY='{{agent_key}}'
  DK_OBSERVABILITY_SERVICE_ACCOUNT_KEY='{{observability_service_account_key}}'
  DK_AZURE_CLIENT_ID='{{auth_azure_client_id}}'
  DK_AZURE_CLIENT_SECRET='{{auth_azure_client_secret}}'
  DK_AZURE_TENANT_ID='{{auth_azure_tenant_id}}'
  DK_DATABRICKS_ENDPOINT='{{databricks_endpoint}}'
  DK_DATABRICKS_METHOD='{{databricks_method}}'
  DK_DATABRICKS_JOBS_VERSION='{{databricks_version}}'
  DK_DATABRICKS_TOKEN='{{databricks_token}}'
  DK_DATABRICKS_HOST='{{databricks_host}}'
  DK_SSIS_DB_HOST='{{ssis_db_host}}'
  DK_SSIS_DB_PORT='{{ssis_db_port}}'
  DK_SSIS_DB_USER='{{ssis_db_user}}'
  DK_SSIS_DB_PASSWORD='{{ssis_db_password}}'
  DK_SSIS_POLLING_INTERVAL='{{ssis_polling_interval}}'
  DK_SYNAPSE_ANALYTICS_WORKSPACE_NAME='{{synapse_analytics_workspace_name}}'
  DK_SYNAPSE_ANALYTICS_SUBSCRIPTION_ID='{{synapse_analytics_subscription_id}}'
  DK_SYNAPSE_ANALYTICS_RESOURCE_GROUP_NAME='{{synapse_analytics_resource_group_name}}'
  DK_SYNAPSE_ANALYTICS_PIPELINES_FILTER='{{synapse_analytics_pipelines_filter}}'
  DK_POWERBI_CLIENT_ID='{{powerbi_client_id}}'
  DK_POWERBI_TENANT_ID='{{powerbi_tenant_id}}'
  DK_POWERBI_USERNAME='{{powerbi_username}}'
  DK_POWERBI_PASSWORD='{{powerbi_password}}'
  DOCKER_IMAGE='{{docker_image}}'
  DOCKER_TAG='{{docker_tag}}'
  DEFAULT_DEPLOYMENT_MODE='{{default_deployment_mode}}'
  DOCKER_EXTRA_ENV_VARS='{{docker_extra_env_vars}}'
  KUBERNETES_EXTRA_ENV_VARS='{{kubernetes_extra_env_vars}}'
  `,
}));

describe('AbstractToolDirective', () => {
  const projectId = '15';
  const mockServiceKeyToken = 'this-is-a-service-key-token';

  @Component({
    selector: 'shell-test-polling-component',
    template: '',
  })
  class TestPollingComponent extends AbstractTool {
    static override _name = 'polling_tool';
    static override _displayName = 'Polling Tool';
    static override _icon = 'polling_tool';
    static override _type = 'POLLING';
    static override _version = 'production';

    override readonly envList = [
      ...this.commonEnvs,
      {
        name: 'DK_API_KEY',
        tpl: 'observability_service_account_key',
        placeholder: '',
        required: true,
      },
      {
        name: 'DK_AGENT_TYPE',
        tpl: 'agent_type',
        placeholder: '',
        required: false,
        formatter: (value: string) => value,
      },
    ];

    override envListForm = new FormGroup({
      ...this.commonEnvsForm.controls,
      DK_API_KEY: new FormControl(),
      DK_AGENT_TYPE: new FormControl('my-agent-type'),
      FLAG: new FormControl(false),
    });

    protected override hidingRules = [
      {when: 'FLAG', equals: true, hide: 'LOGGING_MODE'},
      {when: 'FLAG', equals: false, hide: 'MAX_WORKERS'},
    ];
  }

  @Component({
    selector: 'shell-test-events-component',
    template: '',
  })
  class TestEventsComponent extends AbstractTool {
    static override _name = 'events_tool';
    static override _displayName = 'Events Tool';
    static override _icon = 'events_tool';
    static override _type = 'EVENTS';
    static override _version = 'beta';

    override readonly envList = [ ...this.commonEnvs ];

    override envListForm = new FormGroup({ ...this.commonEnvsForm.controls });

    protected override disableOnStart = [
      this.envListForm.controls['LOGGING_MODE'],
    ];
  }

  let pollingComponent: TestPollingComponent;
  let eventsComponent: TestEventsComponent;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [
        TestPollingComponent,
        TestEventsComponent,
      ],
      providers: [
        MockProvider(ProjectService, class {
          createServiceAccountKey = jest.fn().mockReturnValue(of({token: mockServiceKeyToken}));
        }),
        MockProvider(ProjectStore, class {
          current$ = of({id: projectId});
        }),
        {
          provide: ConfigService,
          useClass: class {
            get = () => 'base';
          }
        },
      ],
    }).compileComponents();

    const pollingComponentFixture = TestBed.createComponent(TestPollingComponent);
    const eventsComponentFixture = TestBed.createComponent(TestEventsComponent);

    pollingComponent = pollingComponentFixture.componentInstance;
    eventsComponent = eventsComponentFixture.componentInstance;

    pollingComponentFixture.detectChanges();
    eventsComponentFixture.detectChanges();
  });

  it('should create', () => {
    expect(pollingComponent).toBeDefined();
    expect(eventsComponent).toBeDefined();
  });

  it('should disable base filled-in fields', () => {
    expect(pollingComponent.envListForm.controls['EXTERNAL_PLUGINS_PATH'].disabled).toBeTruthy();
    expect(pollingComponent.envListForm.controls['ENABLED_PLUGINS'].disabled).toBeTruthy();
    expect(pollingComponent.envListForm.controls['PUBLISH_EVENTS'].disabled).toBeTruthy();
  });

  it('should disable controls specified by base components', () => {
    expect(eventsComponent.envListForm.controls['LOGGING_MODE'].disabled).toBeTruthy();
  });

  it('should initially hide controls specified by base components', () => {
    const env = pollingComponent.envList.find(env => env.name === 'MAX_WORKERS') as any;
    expect(env.hidden).toBeTruthy();
  });

  it('should initially NOT hide controls if the condition is not met', () => {
    const env = pollingComponent.envList.find(env => env.name === 'LOGGING_MODE') as any;
    expect(env.hidden).toBeFalsy();
  });

  it('should hide controls on form value changes', () => {
    pollingComponent.envListForm.patchValue({FLAG: true});

    const env = pollingComponent.envList.find(env => env.name === 'LOGGING_MODE') as any;
    expect(env.hidden).toBeTruthy();
  });

  describe('showStep()', () => {
    it('should update the signal', () => {
      pollingComponent.showStep(3);
      expect(pollingComponent.step()).toEqual(3);
    });
  });

  describe('downloadScript()', () => {
    const fileUrl = 'this-is-a-fake-url';
    const createObjectURL = jest.fn().mockReturnValue(fileUrl);
    const revokeObjectURL = jest.fn();
    let anchor: {href: any; download: any; click: () => any};

    beforeEach(() => {
      anchor = {href: undefined, download: undefined, click: jest.fn()};

      pollingComponent['document'] = {createElement: jest.fn().mockReturnValue(anchor)} as any;

      global.window.URL = {createObjectURL, revokeObjectURL} as any;
      global.window.URL = {createObjectURL, revokeObjectURL} as any;

      pollingComponent.downloadScript();
    });

    it('should create an object URL with a blob object', async () => {
      const [ blob ] = createObjectURL.mock.lastCall;
      expect(blob instanceof Blob).toBeTruthy();
    });

    it('should create and click a dynamic anchor element', () => {
      expect(pollingComponent['document'].createElement).toBeCalledWith('a');
      expect(anchor.href).toEqual(fileUrl);
      expect(anchor.download).toEqual(`deploy-agent-${pollingComponent.name}.sh`);
      expect(anchor.click).toBeCalled();
    });

    it('should revoke the object URL', async () => {
      expect(revokeObjectURL).toBeCalledWith(fileUrl);
    });

    it('should move to deployment step', () => {
      expect(pollingComponent.step()).toEqual(pollingComponent.DeploymentInstructionsStep);
    });

    it('should work the same for events components', () => {
      eventsComponent['document'] = {createElement: jest.fn().mockReturnValue(anchor)} as any;
      eventsComponent.downloadScript();

      expect(eventsComponent.step()).toEqual(eventsComponent.DeploymentInstructionsStep);
    });
  });

  describe('createServiceAccountKey()', () => {
    let projectService: Mocked<ProjectService>;

    beforeEach(() => {
      projectService = TestBed.inject(ProjectService) as Mocked<ProjectService>;
    });

    it('should call the service to create the key', () => {
      const value = {
        name: 'A Name',
        description: 'string',
        expires_after_days: 365,
        allow_send_events: true,
        allow_manage_components: true,
        allow_agent_api: true,
      };
      pollingComponent.serviceKeyControl.setValue(value);
      pollingComponent.createServiceAccountKey();
      expect(projectService.createServiceAccountKey).toBeCalledWith(projectId, {
        name: value.name,
        description: value.description,
        expires_after_days: value.expires_after_days,
        // this theoretically should not be here
        // but the way the other `allow_` fields are excluded from this call
        // is by destructuring from the form fields and now
        // we are not destructing out `allow_age_api` because it is set to `disabled`
        // (for an explanation of which look the comment on there).
        // On the other hand this property won't be used in any call downstream
        allow_agent_api: true,
        allow_send_events: true,
        allowed_services: ['OBSERVABILITY_API', 'EVENTS_API', 'AGENT_API']
      });
    });

    it('should NOT call the service if the key was already created', () => {
      pollingComponent.serviceKeyCreated.set(true);
      pollingComponent.createServiceAccountKey();
      expect(projectService.createServiceAccountKey).not.toBeCalled();
    });

    it('should set the creation flag', () => {
      pollingComponent.createServiceAccountKey();
      expect(pollingComponent.serviceKeyCreated()).toBeTruthy();
    });

    it('should disable the servikey key form controls', () => {
      pollingComponent.createServiceAccountKey();
      expect(pollingComponent.serviceKeyControl.disabled).toBeTruthy();
    });

    describe('for beta agent', () => {
      it('should disable the form control for the events api key', () => {
        eventsComponent.createServiceAccountKey();
        expect(eventsComponent.envListForm.controls['EVENTS_API_KEY'].disabled).toBeTruthy();
      });

      it('should set the value of the form control for the events api key', () => {
        eventsComponent.createServiceAccountKey();
        expect(eventsComponent.envListForm.controls['EVENTS_API_KEY'].value).toEqual(mockServiceKeyToken);
      });
    });

    describe('for production agent', () => {
      it('should disable the form control for the events api key', () => {
        pollingComponent.createServiceAccountKey();
        expect(pollingComponent.envListForm.controls['DK_API_KEY'].disabled).toBeTruthy();
      });

      it('should set the value of the form control for the events api key', () => {
        pollingComponent.createServiceAccountKey();
        expect(pollingComponent.envListForm.controls['DK_API_KEY'].value).toEqual(mockServiceKeyToken);
      });
    });

    it('should move to env variables step', () => {
      pollingComponent.createServiceAccountKey();
      expect(pollingComponent.step()).toEqual(pollingComponent.EnvVariablesStep);
    });
  });
});
