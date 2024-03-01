import { TestBed } from '@angular/core/testing';

import { BasinAlertlvlDcServiceService } from './basin-alertlvl-dc-service.service';

describe('BasinAlertlvlDcServiceService', () => {
  let service: BasinAlertlvlDcServiceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BasinAlertlvlDcServiceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
