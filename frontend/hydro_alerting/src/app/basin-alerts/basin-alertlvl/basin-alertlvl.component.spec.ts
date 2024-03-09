import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BasinAlertlvlComponent } from './basin-alertlvl.component';

describe('BasinAlertlvlComponent', () => {
  let component: BasinAlertlvlComponent;
  let fixture: ComponentFixture<BasinAlertlvlComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BasinAlertlvlComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(BasinAlertlvlComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
