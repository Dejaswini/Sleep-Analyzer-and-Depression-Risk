import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';

// Mock sleep stage data (hypnogram)
const sleepData = [
  { time: '22:00', stage: 0 },
  { time: '22:30', stage: 1 },
  { time: '23:00', stage: 2 },
  { time: '23:30', stage: 3 },
  { time: '00:00', stage: 3 },
  { time: '00:30', stage: 2 },
  { time: '01:00', stage: 4 }, // REM
  { time: '01:30', stage: 2 },
  { time: '02:00', stage: 3 },
  { time: '02:30', stage: 3 },
  { time: '03:00', stage: 2 },
  { time: '03:30', stage: 4 }, // REM
  { time: '04:00', stage: 1 },
  { time: '04:30', stage: 0 }, // Wake
  { time: '05:00', stage: 1 },
  { time: '05:30', stage: 2 },
  { time: '06:00', stage: 1 },
];

const stageLabels = ['Wake', 'N1', 'N2', 'N3', 'REM'];

export const SleepChart = () => {
  return (
    <div className="w-full h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={sleepData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="sleepGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
          <XAxis 
            dataKey="time" 
            stroke="hsl(var(--muted-foreground))"
            style={{ fontSize: '12px' }}
            interval={2}
          />
          <YAxis 
            stroke="hsl(var(--muted-foreground))"
            style={{ fontSize: '12px' }}
            domain={[0, 4]}
            ticks={[0, 1, 2, 3, 4]}
            tickFormatter={(value) => stageLabels[value]}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'hsl(var(--card))',
              border: '1px solid hsl(var(--border))',
              borderRadius: '8px',
              fontSize: '12px'
            }}
            formatter={(value: number) => [stageLabels[value], 'Sleep Stage']}
          />
          <Area 
            type="stepAfter" 
            dataKey="stage" 
            stroke="hsl(var(--primary))" 
            strokeWidth={2}
            fill="url(#sleepGradient)" 
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
