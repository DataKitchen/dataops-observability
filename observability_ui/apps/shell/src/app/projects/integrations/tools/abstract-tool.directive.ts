import { DOCUMENT } from '@angular/common';
import { DestroyRef, Directive, ElementRef, inject, OnInit, QueryList, signal, ViewChildren, effect } from '@angular/core';
import { takeUntilDestroyed, toSignal } from '@angular/core/rxjs-interop';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ConfigService, CustomValidators, difference, ProjectService, ProjectStore, trimStart } from '@observability-ui/core';
import { map, switchMap, take } from 'rxjs';
import scriptTemplateBeta from './agent-script.tpl';
import scriptTemplateProd from './agent-script-v2.tpl';

export interface HidingRule {
  when: string;
  equals: any;
  hide: string;
}

export interface ApiKeyServiceFields {
  name: string;
  description?: string;
  expires_after_days: number;
  allow_send_events: boolean;
  allow_manage_components: boolean;
  allow_agent_api: boolean;
}

@Directive()
export abstract class AbstractTool implements OnInit {
  static readonly _name: string;
  static readonly _displayName: string;
  static readonly _icon: string;
  static readonly _type: string;
  static readonly _image: string;
  static readonly _version: string = 'beta';

  @ViewChildren('envInput') inputElements: QueryList<ElementRef<HTMLInputElement>>;

  readonly ServiceAccountKeyStep = 1;
  readonly EnvVariablesStep = 2;
  readonly DeploymentInstructionsStep = 3;

  protected configService = inject(ConfigService);
  protected projectService = inject(ProjectService);
  protected currentProject$ = inject(ProjectStore).current$;
  private document = inject(DOCUMENT);
  private destroyRef = inject(DestroyRef);

  step = signal(this.ServiceAccountKeyStep);
  creatingServiceKey = signal(false);
  serviceKeyCreated = signal(false);
  serviceKeyControl = new FormControl<ApiKeyServiceFields>({
    name: '',
    expires_after_days: 356,
    description: undefined,
    allow_send_events: true,
    allow_manage_components: true,
    allow_agent_api: true,
  });

  protected project = toSignal(this.currentProject$);
  protected readonly pollingAgentsCommonEnvs = [
    { name: 'POLLING_INTERVAL_SECS', placeholder: '# the polling frequency in seconds', required: true },
    { name: 'MAX_WORKERS', placeholder: '# the number of workers available', required: true },
  ];
  protected readonly eventsAgentsCommonEnvs: any[] = [];
  protected readonly commonEnvs = [
    { name: 'EVENTS_API_HOST', placeholder: '# the base API URL for Observability', required: true },
    { name: 'EVENTS_API_KEY', placeholder: '# an API key for the Observability project', required: true },
    { name: 'EVENTS_PROJECT_ID', placeholder: '# the ID of the Observability project', required: true },
    { name: 'EXTERNAL_PLUGINS_PATH', placeholder: '# the path where any custom plugins can be accessed', required: true },
    { name: 'ENABLED_PLUGINS', placeholder: '', required: true },
    { name: 'PUBLISH_EVENTS', placeholder: '' , required: true},
    { name: 'LOGGING_MODE', placeholder: '# the logging level (DEBUG or INFO)', required: true },
    ...(() => this.type === 'POLLING' ? this.pollingAgentsCommonEnvs : this.eventsAgentsCommonEnvs)()
  ];

  protected readonly pollingAgentsCommonEnvsForm = new FormGroup({
    MAX_WORKERS: new FormControl('10', [ Validators.required, CustomValidators.number, Validators.min(1) ]),
  });
  protected readonly eventsAgentsCommonEnvsForm = new FormGroup({});
  protected readonly commonEnvsForm = new FormGroup({
    EVENTS_API_HOST: new FormControl('', Validators.required),
    EVENTS_API_KEY: new FormControl('', Validators.required),
    EVENTS_PROJECT_ID: new FormControl(undefined, Validators.required),
    EXTERNAL_PLUGINS_PATH: new FormControl('/plugins', Validators.required),
    ENABLED_PLUGINS: new FormControl('', Validators.required),
    PUBLISH_EVENTS: new FormControl('True', Validators.required),
    POLLING_INTERVAL_SECS: new FormControl('10', [ Validators.required, CustomValidators.number, Validators.min(1) ]),
    LOGGING_MODE: new FormControl('INFO', [ Validators.required, CustomValidators.oneOf([ 'INFO', 'DEBUG' ]) ]),
    DOCKER_TAG: new FormControl('', [ Validators.required ]),
    DEFAULT_DEPLOYMENT_MODE: new FormControl('', [ Validators.required, CustomValidators.oneOf([ 'docker', 'kubernetes' ]) ]),
    ...(() => this.type === 'POLLING' ? this.pollingAgentsCommonEnvsForm.controls : this.eventsAgentsCommonEnvsForm.controls)()
  });


  public abstract envListForm: FormGroup;

  protected hidingRules: HidingRule[] = [];
  protected disableOnStart: FormControl[] = [];
  protected requiredFieldsByAuthType: { [ field: string]: Array<'basic' | 'service_principal'> } = {};
  protected readonly abstract envList: Array<{name: string; tpl?: string; placeholder: string; formatter?: (v: string) => string; default?: string; hidden?: boolean; excluded?: boolean}>;

  constructor() {
    effect(() => {
      const project =  this.project();
      const projectFormControl = this.envListForm.get('EVENTS_PROJECT_ID');
      if (project && projectFormControl && projectFormControl.value !== project.id) {
        projectFormControl.setValue(project.id);
      }
    });
  }

  get name(): string {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    return this.constructor._name;
  }

  get image(): string {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    return this.constructor._image;
  }

  get icon(): string {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    return this.constructor._icon;
  }

  get type(): 'POLLING' | 'EVENTS' {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    return this.constructor._type;
  }

  get version(): 'beta' | 'production' {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    return this.constructor._version;
  }

  ngOnInit(): void {
    [
      this.commonEnvsForm.controls['EVENTS_PROJECT_ID'],
      this.commonEnvsForm.controls['EXTERNAL_PLUGINS_PATH'],
      this.commonEnvsForm.controls['ENABLED_PLUGINS'],
      this.commonEnvsForm.controls['PUBLISH_EVENTS'],
      ...(this.disableOnStart ?? []),
    ].forEach(c => c.disable());

    this.applyHidingRules(this.envListForm);
    this.envListForm.valueChanges.pipe(
      takeUntilDestroyed(this.destroyRef),
    ).subscribe(() => this.applyHidingRules(this.envListForm));
  }

  private applyHidingRules(form: FormGroup): void {
    for (const rule of this.hidingRules) {
      const env = this.findEnv(rule.hide);
      if (env) {
        const fieldValue = form.get(rule.when).value;
        env.hidden = [].concat(rule.equals).includes(fieldValue);
      }
    }
  }

  private findEnv(name: string): {name: string; placeholder: string; hidden?: boolean} | undefined {
    return this.envList.find((env) => env.name === name);
  }

  showStep(step: number): void {
    this.step.set(step);
  }

  downloadScript(): void {
    let dockerExtraEnvVars: string = '';
    let kubernetesExtraEnvVars: string = '';
    const valuePerVariable: {[name: string]: string} = {
      // k8s does not like underscores
      target_service: this.name.replaceAll('_', '-'),
      deployment_name: `${this.envListForm.controls['AGENT_TYPE']?.value}-${this.envListForm.controls['AGENT_KEY']?.value}`.replaceAll('_', '-'),
      docker_image: this.image,
      docker_tag: this.envListForm.controls['DOCKER_TAG'].value,
      default_deployment_mode: this.envListForm.controls['DEFAULT_DEPLOYMENT_MODE'].value,
    };

    let fileContents: string = this.version === 'production' ? scriptTemplateProd : scriptTemplateBeta;
    const variableSlotsInTemplate: string[] = fileContents.match(/{{\w+}}/gim).map(item => item.replace('{{', '').replace('}}', '').trim().toLowerCase());

    for (const variable of this.envList) {
      if (!variable.hidden && !variable.excluded) {
        const slotInTemplate = variable.tpl ?? variable.name.toLowerCase();
        let value = this.envListForm.controls[variable.name].value || variable.default || '';
        if (variable.formatter) {
          value = variable.formatter(value);
        }
        valuePerVariable[slotInTemplate] = value;
      }
    }

    const extraVariables = difference(new Set(Object.keys(valuePerVariable)), new Set(variableSlotsInTemplate));

    if (this.version === 'beta') {
      [ dockerExtraEnvVars, kubernetesExtraEnvVars ] = this.formatExtraVariablesForBetaAgent(extraVariables, valuePerVariable);
    } else if (this.version === 'production') {
      [ dockerExtraEnvVars, kubernetesExtraEnvVars ] = this.formatExtraVariablesForProdAgent(extraVariables, valuePerVariable);
    }

    fileContents = fileContents.replace('{{docker_extra_env_vars}}', dockerExtraEnvVars);
    fileContents = fileContents.replace('{{kubernetes_extra_env_vars}}', kubernetesExtraEnvVars);

    for  (const variableName of variableSlotsInTemplate) {
      const variableValue = valuePerVariable[variableName] ?? '';
      fileContents = fileContents.replace(`{{${variableName.toLowerCase()}}}`, `${variableValue}`);
    }

    const blob = new Blob([fileContents], {type: 'text/x-shellscript'});
    const url = window.URL.createObjectURL(blob);
    const anchor = this.document.createElement('a');
    anchor.href = url;
    anchor.download = `deploy-agent-${this.name}.sh`;
    anchor.click();
    window.URL.revokeObjectURL(url);
    this.showStep(this.DeploymentInstructionsStep);
  }

  private formatExtraVariablesForBetaAgent(variables: Set<string>, variablesValues: {[name: string]: string}): [ string, string ] {
    const dockerExtraEnvVars: string[] = [];
    const kubernetesExtraEnvVars: string[] = [];

    for (const variableName of variables) {
      const variableValue = variablesValues[variableName];
      dockerExtraEnvVars.push(`      - ${variableName.toUpperCase()}='${variableValue}'\n`);
      kubernetesExtraEnvVars.push(`  ${variableName.toUpperCase()}: '${variableValue}'\n`);
    }

    return [ dockerExtraEnvVars.join(''), kubernetesExtraEnvVars.join('') ];
  }

  private formatExtraVariablesForProdAgent(variables: Set<string>, variablesValues: {[name: string]: string}): [ string, string ] {
    const dockerExtraEnvVars: string[] = [];
    const kubernetesExtraEnvVars: string[] = [];

    for (const variableName of variables) {
      const variableValue = variablesValues[variableName];
      dockerExtraEnvVars.push(`        "${variableName.toUpperCase()}=${variableValue}"`);
      kubernetesExtraEnvVars.push(`    "${variableName.toUpperCase()}": "${variableValue}"`);
    }

    return [ trimStart(dockerExtraEnvVars.join(',\n')), trimStart(kubernetesExtraEnvVars.join(',\n')) ];
  }

  createServiceAccountKey(): void {
    if (this.serviceKeyCreated()) {
      return;
    }

    const {
      allow_manage_components,
      ...request
    } = this.serviceKeyControl.value;

    const allowedServices: string[] = [];

    if (allow_manage_components) {
      allowedServices.push('OBSERVABILITY_API');
    }

    // since we are creating a new agent we must have this always set
    // in fact we have the checkbox set to true and disabled in service-key-form.component
    // Bear in mind that we are not trying to read the value from the form because
    // it is set to `disabled` so it won't have it
    allowedServices.push('EVENTS_API');
    allowedServices.push('AGENT_API');

    this.creatingServiceKey.set(true);
    this.currentProject$.pipe(
      map((project) => project.id),
      switchMap((projectId) => this.projectService.createServiceAccountKey(projectId, {
        ...request,
        allowed_services: allowedServices
      })),
      take(1),
    ).subscribe((serviceKey) => {
      this.serviceKeyCreated.set(true);
      this.creatingServiceKey.set(false);

      this.serviceKeyControl.disable();

      const serviceAccountKeyFieldname = this.version === 'production' ? 'DK_API_KEY' : 'EVENTS_API_KEY';
      this.setServiceKeyForAgent(serviceKey.token, serviceAccountKeyFieldname);

      this.showStep(this.EnvVariablesStep);
    });
  }

  private setServiceKeyForAgent(serviceKey: string, field: string) {
    this.envListForm.controls[field].disable();
    this.envListForm.patchValue({[field]: serviceKey});
  }
}
