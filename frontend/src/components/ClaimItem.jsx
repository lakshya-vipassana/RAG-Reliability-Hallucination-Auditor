import React, { useState } from "react";
import VerdictBadge from "./VerdictBadge";

function ClaimItem({ claim, evidence }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded shadow">
      <div className="flex justify-between items-start">
        <div className="flex-1 pr-4">
          <div className="font-medium">{claim.text}</div>

          {evidence && (
            <div className="mt-2 space-y-1 text-sm">
              <VerdictBadge supportLevel={evidence.support_level} />

              <div>
                <span className="font-semibold">Confidence:</span>{" "}
                {Math.round((evidence.confidence || 0) * 100)}%
              </div>

              <div>
                <span className="font-semibold">Rationale:</span>{" "}
                {evidence.rationale}
              </div>
            </div>
          )}
        </div>

        <button
          onClick={() => setOpen(!open)}
          className="text-sm text-blue-500"
        >
          {open ? "Hide" : "Details"}
        </button>
      </div>

      {open && evidence?.chunk_ids?.length > 0 && (
        <div className="mt-3 pl-3 border-l border-gray-300 dark:border-gray-600 text-sm">
          <div className="font-semibold mb-1">Evidence Chunk IDs:</div>
          {evidence.chunk_ids.map((id, i) => (
            <div key={i}>{id}</div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ClaimItem;
