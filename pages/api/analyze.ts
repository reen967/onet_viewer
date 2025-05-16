import { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';
import csvParse from 'csv-parse/lib/sync';

const dataDir = path.join(process.cwd(), 'public', 'data');

function loadCSV(fileName: string) {
  const filePath = path.join(dataDir, fileName);
  const content = fs.readFileSync(filePath);
  return csvParse(content, {
    columns: true,
    skip_empty_lines: true,
  });
}

function classifyTask(taskText: string) {
  const lower = taskText.toLowerCase();
  if (lower.includes('enter') || lower.includes('record') || lower.includes('update')) {
    return { isAutomatable: true, tech: 'RPA' };
  } else if (lower.includes('lift') || lower.includes('move') || lower.includes('carry') || lower.includes('transport')) {
    return { isAutomatable: true, tech: 'AGV / Robotic Arm' };
  } else if (lower.includes('inspect') || lower.includes('sort')) {
    return { isAutomatable: true, tech: 'Computer Vision' };
  } else {
    return { isAutomatable: false, tech: 'Human-required' };
  }
}

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  const { soc } = req.query;
  if (!soc || typeof soc !== 'string') return res.status(400).json({ error: 'SOC code required' });

  const tasks = loadCSV('task_statements.csv');

  const relevantTasks = tasks.filter((t: any) => t['O*NET-SOC Code'] === soc);
  const processed = relevantTasks.map((t: any) => {
    const { isAutomatable, tech } = classifyTask(t['Task Title']);
    return {
      id: t['Task ID'],
      text: t['Task Title'],
      isAutomatable,
      suggestedTech: tech,
    };
  });

  const retained = processed.filter((t) => !t.isAutomatable);
  const autoPercent = processed.filter((t) => t.isAutomatable).length / processed.length;

  res.status(200).json({
    tasks: processed,
    retainedTasks: retained,
    automationPercent: autoPercent,
  });
}
