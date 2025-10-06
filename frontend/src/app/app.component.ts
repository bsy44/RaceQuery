import { Component } from '@angular/core';
import {Header} from './shared/components/header/header';
import {RouterOutlet} from '@angular/router';
import {Footer} from './shared/components/footer/footer';

@Component({
  selector: 'app-root',
  imports: [
    Header,
    RouterOutlet,
    Footer
  ],
  standalone: true,
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {}
