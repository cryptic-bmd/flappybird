export function log(message?: unknown, ...optionalParams: unknown[]): void {
  if (import.meta.env.VITE_LOG_TO_CONSOLE === "true") {
    console.log(message, ...optionalParams);
  }
};
