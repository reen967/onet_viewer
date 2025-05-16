import { useState } from 'react';

export default function Home() {
  const [socCode, setSocCode] = useState('');
  const [data, setData] = useState<any>(null);

  const handleAnalyze = async () => {
    const res = await fetch(`/api/analyze?soc=${socCode}`);
    const result = await res.json();
    setData(result);
  };

  return (
    <main className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Role Automation Recomposer</h1>
      <input
        className="border p-2 rounded w-full mb-4"
        placeholder="Enter SOC Code (e.g. 53-7062.00)"
        value={socCode}
        onChange={(e) => setSocCode(e.target.value)}
      />
      <button onClick={handleAnalyze} className="bg-blue-600 text-white px-4 py-2 rounded">
        Analyze
      </button>

      {data && (
        <div className="mt-6">
          <p className="font-semibold mb-2">% Tasks Automatable: {(data.automationPercent * 100).toFixed(1)}%</p>

          <h2 className="text-xl font-bold mt-4 mb-2">Retained Human Tasks</h2>
          <ul className="list-disc list-inside">
            {data.retainedTasks.map((t: any) => (
              <li key={t.id}>{t.text}</li>
            ))}
          </ul>

          <h2 className="text-xl font-bold mt-4 mb-2">Automation Plan (by Task)</h2>
          <ul className="list-disc list-inside">
            {data.tasks.map((t: any) => (
              <li key={t.id}>
                {t.text} — <strong>{t.suggestedTech}</strong>
              </li>
            ))}
          </ul>
        </div>
      )}
    </main>
  );
}

