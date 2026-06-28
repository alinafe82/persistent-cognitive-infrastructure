export const SITE_NAME = "PCI Control Plane";
export const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL ?? "https://pci-control-plane.local";
export const CONTACT_EMAIL =
  process.env.NEXT_PUBLIC_CONTACT_EMAIL ?? "security@pci-control-plane.example";
export const MONETIZATION_MODE =
  process.env.NEXT_PUBLIC_MONETIZATION_MODE ?? "leadgen";

export function siteUrl(path = "/"): string {
  return new URL(path, SITE_URL).toString();
}
