export type Industry = {
  id: number;
  naics_desc: string;
};

export interface State {
  name: string;
  code: string;
}

export interface City {
  city: string;
  county: string;
  latitude: number;
  longitude: number;
  state_code: string;
  zip: number;
}

export interface ChapterType {
  id: number;
  name: string;
}

export interface AmountRange {
  id: number;
  min: number;
  max: number;
}

// user
export type SubscriptionTypes =
  | 'none'
  | 'trial'
  | 'individual'
  | 'team'
  | 'mvp';

export interface User {
  id: number;
  customer_id: string | null;
  subscription_id: string | null;
  subscription_price_id: string | null;
  subscription_price_level: number;
  subscription_status: string | null;
  subscription_inherited: number;
  first_name: string | null;
  last_name: string | null;
  email_address: string;
  company_name: string | null;
  company_sector: number | null;
  company_state: string | null;
  company_zip_code: string | null;
  industry_naics_code: string | null;
  email_alerts_enabled: number;
  email_alert_1: string | null;
  email_alert_2: string | null;
  email_alert_3: string | null;
  text_alerts_enabled: number;
  phone_alert_1: string | null;
  phone_alert_2: string | null;
  phone_alert_3: string | null;
  phone_number: string | null;
  onboarding_completed: number;
  daily: number;
  weekly: number;
  bi_weekly: number;
  is_social: number;
  tos: number;
  product_tour_enabled: number;
  team: string;
  date_added: Date;
  subscription: SubscriptionTypes;
  max_team_count: number;
  case_refresh_count: number;
  case_refresh_max: number;
  file_download_count: number;
  file_download_max: number;
}

// bankruptcy
export interface BankruptcyDetails {
  dci_id: number;
  case_name: string;
  case_number: string;
  company_address: string | null;
  court_id: string | null;
  ein: number | null;
  pdf_filename: string | null;
  industry: string | null;
  city: string | null;
  state_code: string | null;
  cs_chapter: number;
  assets_max: number | null;
  assets_min: number | null;
  creditor_max: number | null;
  creditor_min: number | null;
  liabilities_max: number | null;
  liabilities_min: number | null;
  date_filed: Date;
  date_added: Date;
  total_loss: number;
  is_bankruptcy_watchlisted: 'true' | 'false';
}

export interface BankruptcyRecord {
  dci_id: number;
  case_name: string;
  case_number: string;
  industry: string | null;
  city: string | null;
  state_code: string | null;
  cs_chapter: number;
  assets_max: number | null;
  assets_min: number | null;
  creditor_max: number | null;
  creditor_min: number | null;
  liabilities_max: number | null;
  liabilities_min: number | null;
  is_bankruptcy_watchlisted: 'true' | 'false';
  date_filed: Date;
  date_added: Date;
}

export interface BankruptcyFilters {
  search: string;
  chapterTypes: number[];
  dateAdded: [Date | string | null, Date | string | null];
  dateFiled: [Date | string | null, Date | string | null];
  state: string;
  city: string;
  assetRanges: number[];
  liabilityRanges: number[];
  involuntary: boolean;
  sub_chapv: boolean;
}

export interface BankruptcySorting {
  field: keyof BankruptcyRecord;
  sort: 'asc' | 'desc';
}

export interface BankruptciesResult {
  count: number;
  records: BankruptcyRecord[];
}

//corporate loss
export interface LossRecord {
  id: number;
  city: string | null;
  creditor_name: string;
  case_name: string;
  case_number: string;
  filing_id: number;
  dci_id: number;
  date_filed: Date;
  date_added: Date;
  industry: string | null;
  state_code: string | null;
  unsecured_claim: number;
  is_company_watchlisted: 'true' | 'false';
}

export interface LossFilters {
  search: string;
  loss: [number, number];
  dateAdded: [Date | string | null, Date | string | null];
  dateFiled: [Date | string | null, Date | string | null];
  state: string;
  city: string;
  max_losses_per_case: number | null;
  id: number | null;
}

export interface LossSorting {
  field: keyof LossRecord;
  sort: 'asc' | 'desc';
}

export interface LossesResult {
  count: number;
  records: LossRecord[];
}

export type NotificationType =
  | 'bk'
  | 'activity'
  | 'system'
  | 'refresh_ok'
  | 'refresh_failed';
export type NotificationStatus = 'read' | 'unread';
export interface NotificationRecord {
  id: number;
  title: string;
  body: string;
  status: NotificationStatus;
  type: NotificationType;
  bk_id: string | null;
  activity_id: string | null;
  date: Date;
}

export interface SearchResult {
  bankruptcies: {
    dci_id: number;
    case_name: string;
    total_loss: number;
  }[];
  losses: {
    id: number;
    dci_id: number;
    creditor_name: string;
    unsecured_claim: number;
  }[];
}

export interface News {
  Link: string;
  Snippet: string;
  Title: string;
  date: Date;
}

export type DocketFileTypes = 'petition' | 'creditors' | 'other';

export interface Docket {
  id: number;
  file_type: DocketFileTypes;
  case_id: number;
  activity: string;
  docs: number;
  pages: number;
  doc_url: string | 'None';
  entry_date: string;
  date_added: Date;
}

export interface DocketFile {
  docket_link_id: number;
  filename: string;
  link: string;
}

export interface UserFileAccess {
  docket_entry_id: number;
  docket_entry_link: string;
  docket_entry_name: string;
  file_type: string;
  name: string;
}

export interface SplashItem {
  creditor_name: string;
  industry: string | null;
  unsecured_claim: number;
}
