import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';
import { NgIf } from '@angular/common';

@Component({
  selector: 'app-race-details',
  templateUrl: './race-detail.html',
  imports: [NgIf],
  styleUrls: ['./race-detail.css']
})
export class RaceDetail implements OnInit {
  round!: number;
  season!: number;
  raceData: any;

  constructor(private httpClient: HttpClient, private route: ActivatedRoute) {}

  ngOnInit() {
    this.round = +this.route.snapshot.paramMap.get('round')!;
    this.season = +this.route.snapshot.paramMap.get('season')!;
    console.log()

    this.getRaceDetail();
  }

  goBack() {
    window.history.back();
  }

  getRaceDetail() {
    this.httpClient.get<any[]>(`http://127.0.0.1:5000/races/${this.season}/${this.round}`)
      .subscribe((result: any) => {
        const raceResult = result[0];

        const formatDateRange = (date: string): string => {
          if (!date) return '';
          const start = new Date(date.replace(' ', 'T'));
          if (isNaN(start.getTime())) return '—';

          const weekday = start.toLocaleDateString('fr-FR', { weekday: 'long' });
          const weekdayCapitalized = weekday.charAt(0).toUpperCase() + weekday.slice(1);

          const day = start.getDate().toString().padStart(2, '0');
          const month = start.toLocaleDateString('fr-FR', { month: 'short' })
            .replace('.', '')
            .toUpperCase();

          return `${day} ${month}`;
        };

        const formatTime = (timeStr: string | null | undefined): string | undefined => {
          if (!timeStr) return undefined;

          const match = timeStr.match(/^(\d{2}):(\d{2})/);
          if (!match) return undefined;

          const hours = match[1];
          const minutes = match[2];
          return `${hours}:${minutes}`;
        };

        this.raceData =  {
          circuitName: raceResult.Circuit.circuitName,
          country: raceResult?.Circuit.Location?.country,
          locality: raceResult.Circuit?.Location?.locality,

          fp1Time: formatTime(raceResult.FirstPractice?.time),
          fp1Date: formatDateRange(raceResult.FirstPractice?.date),
          fp2Time: formatTime(raceResult.SecondPractice?.time),
          fp2Date: formatDateRange(raceResult.SecondPractice?.date),
          fp3Time: formatTime(raceResult.ThirdPractice?.time),
          fp3Date: formatDateRange(raceResult.ThirdPractice?.date),

          qualiTime: formatTime(raceResult.Qualifying?.time),
          qualiDate: formatDateRange(raceResult.Qualifying?.date),

          sprintTime: formatTime(raceResult.Sprint?.time),
          sprintDate: formatDateRange(raceResult.Sprint?.date),

          date: formatDateRange(raceResult.date),
          raceName: raceResult.raceName,
          round: +raceResult.round,
          time: formatTime(raceResult.time)
        };
      });
    }
  }
