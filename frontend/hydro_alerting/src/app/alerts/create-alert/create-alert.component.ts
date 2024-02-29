import { Component } from '@angular/core';

@Component({
  selector: 'app-create-alert',
  standalone: true,
  imports: [],
  templateUrl: './create-alert.component.html',
  styleUrl: './create-alert.component.css'
})
export class CreateAlertComponent {


  onSubmitCreate() {
    console.log('Create Alert Form Submitted');
  }

}
