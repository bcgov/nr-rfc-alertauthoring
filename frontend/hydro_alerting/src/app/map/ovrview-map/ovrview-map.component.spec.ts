import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OvrviewMapComponent } from './ovrview-map.component';

describe('OvrviewMapComponent', () => {
  let component: OvrviewMapComponent;
  let fixture: ComponentFixture<OvrviewMapComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OvrviewMapComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(OvrviewMapComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
