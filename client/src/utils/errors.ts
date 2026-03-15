import axios from 'axios';

interface FastAPIErrorDetail {
  type: string;
  loc: (string | number)[];
  msg: string;
  input?: unknown;
}

export function getAxiosError(err: unknown): string {
  let error = "An unknown error occurred";

  if (axios.isAxiosError(err)) {
    const detail = err.response?.data?.detail;

    if (Array.isArray(detail) && detail.length > 0) {
      const messages = (detail as FastAPIErrorDetail[]).map(d => d.msg);
      error = messages.join(", ");
    }
    else if (typeof detail === "string") {
      // HTTPException with string detail
      error = detail;
    }
    else if (typeof err.response?.data?.message === "string") {
      error = err.response.data.message;
    } 
    else {
      error = err.message;
    }
  } else if (err instanceof Error) {
    error = err.message;
  }

  return error
}
