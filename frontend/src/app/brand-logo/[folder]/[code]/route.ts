import { promises as fs } from "node:fs";
import path from "node:path";

export const dynamic = "force-dynamic";

const PUBLIC_BRAND_ROOT = path.join(process.cwd(), "public", "brand");
const ALLOWED_FOLDERS = new Set(["institutions", "careers"]);
const CONTENT_TYPES: Record<string, string> = {
  svg: "image/svg+xml; charset=utf-8",
  png: "image/png",
};

function cleanSegment(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9_-]/g, "");
}

function placeholderSvg(label: string) {
  const safeLabel = label.replace(/[<>&"']/g, "");
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 160" role="img" aria-label="${safeLabel}">
  <rect width="160" height="160" rx="80" fill="#F8F4EA"/>
  <rect x="6" y="6" width="148" height="148" rx="74" fill="none" stroke="#BC955C" stroke-width="4"/>
  <text x="80" y="89" text-anchor="middle" font-family="Arial, sans-serif" font-size="34" font-weight="700" fill="#611232">${safeLabel}</text>
</svg>`;
}

export async function GET(_request: Request, context: { params: Promise<{ folder: string; code: string }> }) {
  const { folder, code } = await context.params;
  const safeFolder = cleanSegment(folder);
  const safeCode = cleanSegment(code);

  if (!ALLOWED_FOLDERS.has(safeFolder) || !safeCode) {
    return new Response(placeholderSvg("SCA"), {
      headers: { "Content-Type": CONTENT_TYPES.svg, "Cache-Control": "no-store" },
    });
  }

  for (const extension of ["svg", "png"]) {
    const logoPath = path.join(PUBLIC_BRAND_ROOT, safeFolder, `${safeCode}.${extension}`);
    if (!logoPath.startsWith(path.join(PUBLIC_BRAND_ROOT, safeFolder))) continue;

    try {
      const file = await fs.readFile(logoPath);
      return new Response(file, {
        headers: {
          "Content-Type": CONTENT_TYPES[extension],
          "Cache-Control": "no-store",
        },
      });
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== "ENOENT") {
        return new Response(placeholderSvg(safeCode.toUpperCase()), {
          headers: { "Content-Type": CONTENT_TYPES.svg, "Cache-Control": "no-store" },
        });
      }
    }
  }

  return new Response(placeholderSvg(safeCode.toUpperCase()), {
    headers: { "Content-Type": CONTENT_TYPES.svg, "Cache-Control": "no-store" },
  });
}
