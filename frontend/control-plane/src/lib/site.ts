export const SITE_NAME = "PCI Control Plane";
export const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL ?? "https://pci-control-plane.local";
export const CONTACT_EMAIL =
  process.env.NEXT_PUBLIC_CONTACT_EMAIL ?? "security@pci-control-plane.example";
export const MONETIZATION_MODE =
  process.env.NEXT_PUBLIC_MONETIZATION_MODE ?? "leadgen";
const configuredGoogleAnalyticsId =
  process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID?.trim() ?? "";
export const GOOGLE_ANALYTICS_ID = /^G-[A-Z0-9]+$/i.test(configuredGoogleAnalyticsId)
  ? configuredGoogleAnalyticsId
  : "";
export const GOOGLE_ANALYTICS_ENABLED = GOOGLE_ANALYTICS_ID.length > 0;
const configuredGoogleTagManagerId = process.env.NEXT_PUBLIC_GTM_ID?.trim() ?? "";
export const GOOGLE_TAG_MANAGER_ID = /^GTM-[A-Z0-9]+$/i.test(
  configuredGoogleTagManagerId
)
  ? configuredGoogleTagManagerId
  : "";
export const GOOGLE_TAG_MANAGER_ENABLED = GOOGLE_TAG_MANAGER_ID.length > 0;

export function siteUrl(path = "/"): string {
  return new URL(path, SITE_URL).toString();
}
