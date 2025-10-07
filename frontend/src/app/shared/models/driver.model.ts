export interface Driver {
  driver: {
    fullName: string;       
    nationality: string;
    code?: string;
    permanentNumber?: string;
    dateOfBirth?: string;
  };
  constructor: string[];
  points: string;
  points_diff: string;
  teamLogo?: string;
}
