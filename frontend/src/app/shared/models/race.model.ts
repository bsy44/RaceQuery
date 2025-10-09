export interface RaceDetail {
  Circuit: {
    Location: {
      country: string;
      locality: string;
    };
    circuitName: string;
  };
  FirstPractice: {
    date: string;
    time: string;
  };
  SecondPractice: {
    date: string;
    time: string;
  };
  ThirdPractice: {
    date: string;
    time: string;
  };
  Qualifying: {
    date: string;
    time: string;
  };
  Sprint: {
    date: string | null;
    time: string | null;
  };
  date: string;
  raceName: string;
  round: string;
  time: string;
  isFinished:boolean;
  isSprint: boolean;
}
