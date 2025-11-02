import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, Activity, Moon, Heart, AlertCircle, Upload } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { SleepChart } from "./SleepChart";
import { HeartRateChart } from "./HeartRateChart";

interface AnalysisResult {
  subjectId: string;
  depressionProbability: number;
  totalSleepTime: number;
  remSleepDuration: number;
  awakenings: number;
  averageHeartRate: number;
}

interface ResultsDisplayProps {
  result: AnalysisResult;
  onNewAnalysis: () => void;
}

export const ResultsDisplay = ({ result, onNewAnalysis }: ResultsDisplayProps) => {
  const getRiskLevel = (probability: number) => {
    if (probability >= 0.7) return { text: "High Risk", variant: "destructive" as const };
    if (probability >= 0.4) return { text: "Moderate Risk", variant: "warning" as const };
    return { text: "Low Risk", variant: "success" as const };
  };

  const riskLevel = getRiskLevel(result.depressionProbability);

  const handleDownload = () => {
    // Mock PDF download - in real app, this would generate actual PDF
    const reportData = `
Sleep & Mental Health Analysis Report
=====================================
Subject ID: ${result.subjectId}
Depression Probability: ${(result.depressionProbability * 100).toFixed(0)}% (${riskLevel.text})
Total Sleep Time: ${result.totalSleepTime} hrs
REM Sleep Duration: ${result.remSleepDuration} hrs
Awakenings: ${result.awakenings}
Average Heart Rate: ${result.averageHeartRate} bpm
    `;
    
    const blob = new Blob([reportData], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sleep-analysis-${result.subjectId}.txt`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <Card className="p-8 shadow-medical border-border/50 bg-gradient-card">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-foreground mb-1">Analysis Results</h2>
            <p className="text-muted-foreground">Subject: {result.subjectId}</p>
          </div>
          <Button onClick={handleDownload} variant="outline" className="gap-2">
            <Download className="h-4 w-4" />
            Download Report
          </Button>
        </div>

        <div className="space-y-6">
          {/* Depression Risk */}
          <div className="flex items-center justify-between p-6 rounded-xl bg-background border border-border/50">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-lg ${
                riskLevel.variant === "destructive" ? "bg-destructive/10" :
                riskLevel.variant === "warning" ? "bg-warning/10" :
                "bg-success/10"
              }`}>
                <AlertCircle className={`h-6 w-6 ${
                  riskLevel.variant === "destructive" ? "text-destructive" :
                  riskLevel.variant === "warning" ? "text-warning" :
                  "text-success"
                }`} />
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Depression Probability</p>
                <p className="text-2xl font-bold">{(result.depressionProbability * 100).toFixed(0)}%</p>
              </div>
            </div>
            <Badge variant={riskLevel.variant} className="text-sm px-4 py-2">
              {riskLevel.text}
            </Badge>
          </div>

          {/* Sleep Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <MetricCard
              icon={<Moon className="h-5 w-5 text-primary" />}
              label="Total Sleep Time"
              value={`${result.totalSleepTime} hrs`}
            />
            <MetricCard
              icon={<Activity className="h-5 w-5 text-accent" />}
              label="REM Sleep Duration"
              value={`${result.remSleepDuration} hrs`}
            />
            <MetricCard
              icon={<AlertCircle className="h-5 w-5 text-warning" />}
              label="Awakenings"
              value={result.awakenings.toString()}
            />
            <MetricCard
              icon={<Heart className="h-5 w-5 text-destructive" />}
              label="Average Heart Rate"
              value={`${result.averageHeartRate} bpm`}
            />
          </div>
        </div>
      </Card>

      {/* Visualizations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6 shadow-card border-border/50 bg-card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Moon className="h-5 w-5 text-primary" />
            Sleep Stage Hypnogram
          </h3>
          <SleepChart />
        </Card>

        <Card className="p-6 shadow-card border-border/50 bg-card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Heart className="h-5 w-5 text-destructive" />
            Heart Rate Trend
          </h3>
          <HeartRateChart averageRate={result.averageHeartRate} />
        </Card>
      </div>

      <div className="flex justify-center pt-4">
        <Button
          onClick={onNewAnalysis}
          variant="outline"
          size="lg"
          className="gap-2 border-primary/50 hover:bg-primary/5"
        >
          <Upload className="h-4 w-4" />
          Analyze Another File
        </Button>
      </div>
    </div>
  );
};

const MetricCard = ({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) => (
  <div className="flex items-center gap-3 p-5 rounded-lg bg-background border border-border/50 hover:shadow-card transition-shadow">
    <div className="p-2 rounded-lg bg-muted/50">
      {icon}
    </div>
    <div>
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="text-xl font-semibold">{value}</p>
    </div>
  </div>
);
