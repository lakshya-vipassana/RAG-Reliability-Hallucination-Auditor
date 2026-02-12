import React, { useState, useEffect } from 'react';
import FailureExplorer from './components/FailureExplorer';
import FinalVerdict from './components/FinalVerdict';
import ClaimList from './components/ClaimList';
import { FaSun, FaMoon } from 'react-icons/fa';
const [dataEvidence, setDataEvidence] = useState([]);

function App() {
  const [theme, setTheme] = useState('');
  const [view, setView] = useState('explorer');
  const [answerText, setAnswerText] = useState('');
  const [claims, setClaims] = useState([]);
  const [finalScore, setFinalScore] = useState(0);
  const [finalVerdict, setFinalVerdict] = useState('');
  const [finalSummary, setFinalSummary] = useState('');
  const [reasons, setReasons] = useState([]);

  // Apply or remove 'dark' class on <html> based on theme state
  useEffect(() => {
    const root = window.document.documentElement;
    if (theme === 'dark') root.classList.add('dark');
    else root.classList.remove('dark');
  }, [theme]);

  // Simulate analysis by splitting the answer into claims
  const handleAnalyze = async () => {
  try {
    const response = await fetch("http://127.0.0.1:8000/audit", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query: answerText,
        answer: answerText, // adjust if backend only uses query
      }),
    });

    const data = await response.json();

    // Claims from backend
    setClaims(data.claims || []);

    // Store evidence separately
    setDataEvidence(data.evidence || []);

    // Metrics
    const faithfulness = data.metrics?.faithfulness || 0;
    setFinalScore(Math.round(faithfulness * 100));

    // Verdict from backend (IMPORTANT)
    setFinalVerdict(data.verdict || "UNKNOWN");

    // Generate reasons based on backend evidence
    const bulletPoints = [];

    (data.evidence || []).forEach((e) => {
      if (e.support_level === "contradicted") {
        bulletPoints.push(`Claim ${e.claim_id} contradicts evidence.`);
      }
      if (e.support_level === "unsupported") {
        bulletPoints.push(`Claim ${e.claim_id} lacks supporting evidence.`);
      }
      if (e.support_level === "weak") {
        bulletPoints.push(`Claim ${e.claim_id} is weakly supported.`);
      }
    });

    setReasons(bulletPoints);

  } catch (error) {
    console.error("Audit failed:", error);
  }
};


  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      {/* Header with title and controls */}
      <header className="p-4 flex justify-between items-center bg-white dark:bg-gray-800 shadow">
        <h1 className="text-xl font-bold">
          {view === 'explorer' ? 'Failure Case Explorer' : 'LLM Answer Safety Report'}
        </h1>
        <div className="flex items-center space-x-4">
          {view === 'report' && (
            <button onClick={() => setView('explorer')} className="text-sm text-blue-500">
              Back to Explorer
            </button>
          )}
          {view === 'explorer' && (
            <button onClick={() => setView('report')} className="text-sm text-blue-500">
              Go to Safety Report
            </button>
          )}
          <button onClick={() => setTheme(theme === 'dark' ? '' : 'dark')}>
            {theme === 'dark' ? (
              <FaSun className="text-yellow-400" />
            ) : (
              <FaMoon className="text-gray-700" />
            )}
          </button>
        </div>
      </header>

      {/* Main content */}
      {view === 'explorer' ? (
        <FailureExplorer />
      ) : (
        <div className="p-4">
          {/* Textarea for user to paste model answer */}
          <textarea
            className="w-full p-2 mb-4 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded"
            rows={4}
            placeholder="Paste model-generated answer here..."
            value={answerText}
            onChange={e => setAnswerText(e.target.value)}
          />
          <button onClick={handleAnalyze} className="px-4 py-2 bg-blue-600 text-white rounded">
            Analyze Answer
          </button>

          {claims.length > 0 && (
            <>
              {/* Final Verdict */}
              <FinalVerdict score={finalScore} verdict={finalVerdict} summary={finalSummary} />

              {/* List of claims */}
              <ClaimList claims={claims} />

              {/* Why Unsafe reasons */}
              <div className="mt-6">
                <h3 className="text-xl font-semibold mb-2">Why this answer is unsafe</h3>
                <ul className="list-disc list-inside space-y-1 text-gray-700 dark:text-gray-300">
                  {reasons.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
