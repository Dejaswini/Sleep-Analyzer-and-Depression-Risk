import { useState } from "react";
import { Brain, Activity } from "lucide-react";
import { UploadSection } from "@/components/UploadSection";
import { ResultsDisplay } from "@/components/ResultsDisplay";

interface AnalysisResult {
  subjectId: string;
  depressionProbability: number;
  totalSleepTime: number;
  remSleepDuration: number;
  awakenings: number;
  averageHeartRate: number;
}

const Index = () => {
  const [showResults, setShowResults] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  const handleAnalyze = (file: File, subjectId: string) => {
    // Mock analysis result - in production, this would call backend API
    const mockResult: AnalysisResult = {
      subjectId,
      depressionProbability: 0.82,
      totalSleepTime: 6.5,
      remSleepDuration: 1.2,
      awakenings: 4,
      averageHeartRate: 72,
    };

    setAnalysisResult(mockResult);
    setShowResults(true);
  };

  const handleNewAnalysis = () => {
    setShowResults(false);
    setAnalysisResult(null);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border/50 bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-primary">
              <Brain className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">Sleep & Mental Health Analyzer</h1>
              <p className="text-sm text-muted-foreground">EEG-based depression risk assessment</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12">
        {!showResults ? (
          <div className="max-w-2xl mx-auto space-y-8">
            {/* Hero Section */}
            <div className="text-center space-y-4 mb-12">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-4">
                <Activity className="h-4 w-4" />
                Advanced EEG Analysis
              </div>
              <h2 className="text-4xl md:text-5xl font-bold text-foreground leading-tight">
                Analyze Sleep Patterns &
                <br />
                <span className="text-transparent bg-clip-text bg-gradient-primary">
                  Depression Risk
                </span>
              </h2>
              <p className="text-lg text-muted-foreground max-w-xl mx-auto">
                Upload your EEG recording from the DREAMT dataset to receive a comprehensive report on sleep quality and mental health indicators.
              </p>
            </div>

            {/* Upload Form */}
            <UploadSection onAnalyze={handleAnalyze} />

            {/* Features */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-8">
              <FeatureCard
                title="Sleep Analysis"
                description="Detailed breakdown of sleep stages and quality metrics"
              />
              <FeatureCard
                title="Risk Assessment"
                description="AI-powered depression probability calculation"
              />
              <FeatureCard
                title="Health Insights"
                description="Heart rate monitoring and awakening patterns"
              />
            </div>
          </div>
        ) : (
          <div className="max-w-6xl mx-auto">
            {analysisResult && (
              <ResultsDisplay result={analysisResult} onNewAnalysis={handleNewAnalysis} />
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-border/50 mt-20 py-8">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>Sleep & Mental Health Analyzer • EEG Data Analysis Platform</p>
          <p className="mt-2">For research and clinical assessment purposes</p>
        </div>
      </footer>
    </div>
  );
};

const FeatureCard = ({ title, description }: { title: string; description: string }) => (
  <div className="p-4 rounded-lg bg-card border border-border/50 text-center hover:shadow-card transition-shadow">
    <h3 className="font-semibold text-foreground mb-2">{title}</h3>
    <p className="text-sm text-muted-foreground">{description}</p>
  </div>
);

export default Index;
