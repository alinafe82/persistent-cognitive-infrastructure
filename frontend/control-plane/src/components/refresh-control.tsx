"use client";

import { RefreshCw } from "lucide-react";
import { useState } from "react";

export function RefreshControl() {
  const [isPending, setIsPending] = useState(false);

  return (
    <form
      action="/"
      method="get"
      className="flex min-w-36 flex-col items-end gap-1"
      onSubmit={() => setIsPending(true)}
    >
      <button
        type="submit"
        className="refresh-button inline-flex items-center gap-2 rounded-md border border-line bg-white px-3 py-2 text-sm font-medium text-ink disabled:cursor-wait disabled:opacity-70"
        disabled={isPending}
        aria-busy={isPending}
      >
        <RefreshCw className={`h-4 w-4 ${isPending ? "animate-spin" : ""}`} aria-hidden="true" />
        {isPending ? "Refreshing…" : "Refresh state"}
      </button>
      <span className="min-h-4 text-xs text-graphite" role="status" aria-live="polite">
        {isPending ? "Requesting latest state…" : ""}
      </span>
    </form>
  );
}
