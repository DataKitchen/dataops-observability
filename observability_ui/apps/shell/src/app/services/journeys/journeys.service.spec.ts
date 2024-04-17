import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ComponentType, ConfigService } from '@observability-ui/core';
import { JourneysService } from './journeys.service';
import { componentsByJourney } from './journeys.mock';

describe('Journeys Service', () => {
  const journeyId = '1';
  let service: JourneysService;
  let httpClient: HttpTestingController;

  const components = componentsByJourney;

  jest.spyOn(console, 'info').mockImplementation();

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ HttpClientTestingModule ],
      declarations: [],
      providers: [
        JourneysService,
        {
          provide: ConfigService,
          useClass: class {
            get = () => 'base';
          }
        },
      ]
    });

    service = TestBed.inject(JourneysService);
    httpClient = TestBed.inject(HttpTestingController);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('create()', () => {
    it('should exclude instance_rules from the payload', (done) => {
      service.create({
        name: 'Something',
        description: 'A description',
        instance_rules: [ {} as any ],
      }, '1').subscribe((resp) => {
        expect(resp).toBe(components.entities[0]);
        done();
      });

      const request = httpClient.expectOne(request =>
        request.url === 'base/observability/v1/projects/1/journeys'
        && request.method === 'POST'
        && request.body.instance_conditions === undefined
      );
      request.flush(components.entities[0]);
    });
  });

  describe('deleteInstanceRule()', () => {
    it('should delete a rule by id', () => {
      service.deleteInstanceRule('15').subscribe();
      httpClient.expectOne({
        url: 'base/observability/v1/instance-conditions/15',
        method: 'DELETE',
      }).flush({});
    });
  });

  describe('update()', () => {
    it('should exclude instance_rules from the payload', (done) => {
      service.update({
        id: '2',
        name: 'Something',
        description: 'A description',
        instance_rules: [ {} as any ],
      }).subscribe((resp) => {
        expect(resp).toBe(components.entities[0]);
        done();
      });

      const request = httpClient.expectOne(request =>
        request.url === 'base/observability/v1/journeys/2'
        && request.method === 'PATCH'
        && request.body.instance_conditions === undefined
      );
      request.flush(components.entities[0]);
    });
  });

  describe('getComponentsByJourney()', () => {
    it('should get all components for this journey', (done) => {

      service.getComponentsByJourney('id', {component_type: [ ComponentType.BatchPipeline, ComponentType.Dataset ]}).subscribe((resp) => {
        expect(resp).toEqual(components);
        done();
      });

      const request1 = httpClient.expectOne('base/observability/v1/journeys/id/components?component_type=BATCH_PIPELINE&component_type=DATASET&count=0');
      request1.flush({
        entities: [],
        total: 2,
      });

      const request2 = httpClient.expectOne('base/observability/v1/journeys/id/components?component_type=BATCH_PIPELINE&component_type=DATASET&count=2');
      request2.flush(components);

    });
  });

  describe('getJourneyDag()', () => {
    it('should get the dag from the API', () => {
      service.getJourneyDag(journeyId).subscribe();
      httpClient.expectOne({
        method: 'GET',
        url: `base/observability/v1/journeys/${journeyId}/dag`,
      });
    });
  });

  describe('createJourneyDagEdge()', () => {
    it('should create a new edge in the journey dag', () => {
      const left = 'node-1';
      const right = 'node-2';

      service.createJourneyDagEdge(journeyId, left, right).subscribe();
      httpClient.expectOne(request =>
        request.url === `base/observability/v1/journeys/${journeyId}/dag`
          && request.method === 'PUT'
          && request.body.left === left
          && request.body.right === right
      );
    });

    it('should create a new edge missing the left vertex', () => {
      const right = 'node-2';

      service.createJourneyDagEdge(journeyId, undefined, right).subscribe();
      httpClient.expectOne(request =>
        request.url === `base/observability/v1/journeys/${journeyId}/dag`
          && request.method === 'PUT'
          && request.body.left === undefined
          && request.body.right === right
      );
    });
  });

  describe('deleteJourneyDagEdge()', () => {
    it('should delete an edge from the journey dag', () => {
      const id = '2';

      service.deleteJourneyDagEdge(id).subscribe();
      httpClient.expectOne({
        url: `base/observability/v1/journey-dag-edge/${id}`,
        method: 'DELETE',
      });
    });
  });
});
