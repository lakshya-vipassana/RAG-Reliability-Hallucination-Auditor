import React from "react";

function FinalVerdict({ verdict, metrics }) {
  let color = "text-gray-600";

  if (verdict === "SAFE") {
    color = "text-green-600";
  } else if (verdict === "PARTIALLY_SUPPORTED") {
    color = "text-yellow-600";
  } else if (verdict === "UNSAFE") {
    color = "text-red-600";
  }

  return (
    <div className="mt-6 p-4 bg-white dark:bg-gray-800 rounded-lg shadow">
      <h2 className="text-lg font-bold mb-3">Final Verdict</h2>

      <div className={`text-3xl font-bold ${color}`}>
        {verdict}
      </div>

      {metrics && (
        <div className="mt-4 space-y-1 text-sm">
          <div>
            <span className="font-semibold">Faithfulness:</span>{" "}
            {Math.round((metrics.faithfulness || 0) * 100)}%
          </div>
          <div>
            <span className="font-semibold">Hallucination Rate:</span>{" "}
            {Math.round((metrics.hallucination_rate || 0) * 100)}%
          </div>
          <div>
            <span className="font-semibold">Evidence Coverage:</span>{" "}
            {Math.round((metrics.evidence_coverage || 0) * 100)}%
          </div>
        </div>
      )}
    </div>
  );
}

export default FinalVerdict;
