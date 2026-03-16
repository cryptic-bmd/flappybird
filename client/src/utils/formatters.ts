export function formatTwoDecimalsExact(num: number | null | undefined): string {
  if (num === null || num === undefined || isNaN(num)) return "0.00";
  
  const [integer, fraction = ""] = String(num).split(".");
  const paddedFraction = (fraction + "00").slice(0, 2); // No rounding
  return `${Number(integer).toLocaleString()}.${paddedFraction}`;
}

export function truncateStrings(word: string, sliceLength: number = 5): string {
  return word.length > 20 ? `${word.slice(0, sliceLength)}...${word.slice(-sliceLength)}` : word;
}
