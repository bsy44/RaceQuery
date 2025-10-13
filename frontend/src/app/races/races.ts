import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { COUNTRY_TO_ISO } from '../shared/nationalities';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SelectorYears } from '../shared/components/selector-years/selector-years';
import { RouterLink } from '@angular/router';
import { RaceDetail } from '../shared/models/race.model';

@Component({
  selector: 'app-events',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    SelectorYears,
    RouterLink
  ],
  templateUrl: './races.html',
  styleUrl: './races.css'
})

export class Races implements OnInit{
  years: number [] = [];
  raceList: any[] = [];
  selectedYear: number = new Date().getFullYear();

  constructor(private http:HttpClient) {}

  ngOnInit() {
    const currentYear = new Date().getFullYear();
    this.years = Array.from({length: currentYear - 2024 + 1}, (_, i) => 2024 + i).reverse();
    this.getRaces();
  }

  getRaces() {
    this.http.get(`http://127.0.0.1:5000/events/${this.selectedYear}`).subscribe((result: any) => {
      this.raceList = (result || []).map((race: any) => {
        console.log(race);

        const formatDateRange = (
          sessions: any[] | undefined,
          raceEndStr: string | null | undefined
        ): string => {
          if (!sessions || sessions.length === 0) return '—';

          const fp1 = sessions.find(s => s.name?.toLowerCase().includes('fp1')) || sessions[0];
          const startStr = fp1?.local_date;
          const endStr = raceEndStr;

          if (!startStr || !endStr) return '—';
          const start = new Date(startStr.replace(' ', 'T'));
          const end = new Date(endStr.replace(' ', 'T'));

          if (isNaN(start.getTime()) || isNaN(end.getTime())) return '—';

          const startDay = start.getDate().toString().padStart(2, '0');
          const endDay = end.getDate().toString().padStart(2, '0');
          const month = end.toLocaleDateString('fr-FR', { month: 'short' })
            .replace('.', '')
            .toUpperCase();

          return `${startDay} - ${endDay} ${month}`;
        };

        return {
          circuitName: race.circuit_name,
          country: race.country,
          eventDate: formatDateRange(race.sessions, race.event_date),
          location: race.location,
          round: race.round,
          season: race.season,
          gpName: race.short_name,
          sessions: race.sessions,
          eventFormat: race.event_format
        };
      });
    });
  }

  getFlagClass(country: string): string {
    return  COUNTRY_TO_ISO[country] || 'xx';
  }
}
