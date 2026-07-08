/**
 * Export helpers for saving a conversation.
 *
 * - exportAsText: builds a plain-text transcript and triggers a download.
 *   Zero dependencies, works everywhere.
 * - exportAsPDF: opens the browser's print dialog with a print-only
 *   stylesheet (see App.css `@media print`), so the user can "Save as PDF"
 *   from there. This avoids pulling in a heavy client-side PDF library just
 *   for this — every browser already has a solid PDF-via-print path.
 */
export function exportAsText(messages, title = "Conversation") {
  const lines = [title, `Exported ${new Date().toLocaleString()}`, "".padEnd(40, "-"), ""];

  for (const m of messages) {
    const speaker = m.role === "user" ? "You" : "Assistant";
    lines.push(`${speaker}:`);
    lines.push(m.content || "");
    lines.push("");
  }

  const blob = new Blob([lines.join("\n")], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${title.replace(/\s+/g, "-").toLowerCase()}.txt`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export function exportAsPDF() {
  // The actual "export" happens via the browser's native print-to-PDF,
  // triggered by window.print(). App.css's @media print rules hide
  // everything except the message list for a clean result.
  window.print();
}
