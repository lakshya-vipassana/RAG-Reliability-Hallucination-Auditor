import React from "react";
import ClaimItem from "./ClaimItem";

function ClaimList({ claims, evidence }) {
  return (
    <div className="mt-4 space-y-4 overflow-y-auto max-h-[400px]">
      {claims.map((claim) => {
        const claimEvidence = evidence.find(
          (e) => e.claim_id === claim.id
        );

        return (
          <ClaimItem
            key={claim.id}
            claim={claim}
            evidence={claimEvidence}
          />
        );
      })}
    </div>
  );
}

export default ClaimList;
