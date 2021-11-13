import { TestBed } from '@angular/core/testing';

import { AsyncBusService } from './async-bus.service';

describe('AsyncBusService', () => {
  let service: AsyncBusService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AsyncBusService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
