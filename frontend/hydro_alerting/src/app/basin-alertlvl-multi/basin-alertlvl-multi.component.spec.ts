import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BasinAlertlvlMultiComponent } from './basin-alertlvl-multi.component';

describe('BasinAlertlvlMultiComponent', () => {
  let component: BasinAlertlvlMultiComponent;
  let fixture: ComponentFixture<BasinAlertlvlMultiComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BasinAlertlvlMultiComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(BasinAlertlvlMultiComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
