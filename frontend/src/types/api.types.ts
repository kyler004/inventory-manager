// These mirror our data models exactly — type safety across the entire frontend.
// standard response envelopes from our API design
export interface APiResponse<T> {
  status: "success" | "error";
  data: T;
}

export interface PaginatedResponse<T> {
  status: "success";
  data: T[];
  meta: {
    page: number;
    page_size: number;
    total_count: number;
    total_pages: number;
  };
}

export interface ApiError {
  status: "error";
  code: string;
  message: string;
  details?: Record<string, unknown>;
}
