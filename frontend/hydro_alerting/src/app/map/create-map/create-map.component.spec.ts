import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateMapComponent } from './create-map.component';

describe('CreateMapComponent', () => {
  let component: CreateMapComponent;
  let fixture: ComponentFixture<CreateMapComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CreateMapComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(CreateMapComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
