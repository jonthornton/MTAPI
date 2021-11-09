import { TestBed } from '@angular/core/testing';

import { AsyncTrainService } from './async-train.service';

describe('AsyncTrainService', () => {
  let service: AsyncTrainService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AsyncTrainService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
