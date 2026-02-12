import React from "react";

function VerdictBadge({ supportLevel }) {
  let colorClasses = "bg-gray-500 text-white";

  if (supportLevel === "supported") {
    colorClasses = "bg-green-600 text-white";
  } else if (supportLevel === "weak") {
    colorClasses = "bg-yellow-500 text-white";
  } else if (supportLevel === "unsupported") {
    colorClasses = "bg-orange-600 text-white";
  } else if (supportLevel === "contradicted") {
    colorClasses = "bg-red-600 text-white";
  }

  return (
    <span
      className={`inline-block px-2 py-1 text-xs font-semibold rounded ${colorClasses}`}
    >
      {supportLevel}
    </span>
  );
}

export default VerdictBadge;
