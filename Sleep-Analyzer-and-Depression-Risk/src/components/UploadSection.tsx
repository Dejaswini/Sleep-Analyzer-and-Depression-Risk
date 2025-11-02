import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Upload, FileText } from "lucide-react";
import { toast } from "sonner";

interface UploadSectionProps {
  onAnalyze: (file: File, subjectId: string) => void;
}

export const UploadSection = ({ onAnalyze }: UploadSectionProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [subjectId, setSubjectId] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      const fileExtension = selectedFile.name.split('.').pop()?.toLowerCase();
      if (fileExtension === 'edf' || fileExtension === 'npy') {
        setFile(selectedFile);
        toast.success("File uploaded successfully");
      } else {
        toast.error("Please upload a .edf or .npy file");
      }
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      toast.error("Please upload an EEG data file");
      return;
    }
    if (!subjectId.trim()) {
      toast.error("Please enter a subject ID");
      return;
    }
    
    setIsLoading(true);
    // Simulate processing delay
    setTimeout(() => {
      onAnalyze(file, subjectId);
      setIsLoading(false);
    }, 1500);
  };

  return (
    <Card className="p-8 shadow-medical border-border/50 bg-gradient-card">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-3">
          <Label htmlFor="eeg-file" className="text-base font-medium">
            Upload EEG Data File
          </Label>
          <div className="relative">
            <Input
              id="eeg-file"
              type="file"
              accept=".edf,.npy"
              onChange={handleFileChange}
              className="cursor-pointer file:cursor-pointer file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-primary file:text-primary-foreground hover:file:bg-primary/90 transition-all"
            />
            <div className="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
              {file ? (
                <>
                  <FileText className="h-4 w-4 text-success" />
                  <span className="text-foreground font-medium">{file.name}</span>
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4" />
                  <span>Supported formats: .edf, .npy</span>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <Label htmlFor="subject-id" className="text-base font-medium">
            Enter Subject ID
          </Label>
          <Input
            id="subject-id"
            type="text"
            placeholder="e.g., 001"
            value={subjectId}
            onChange={(e) => setSubjectId(e.target.value)}
            className="text-base"
            required
          />
        </div>

        <Button
          type="submit"
          size="lg"
          disabled={isLoading}
          className="w-full bg-gradient-primary hover:opacity-90 transition-opacity text-base font-medium shadow-medical"
        >
          {isLoading ? "Processing..." : "Analyze Sleep and Depression Risk"}
        </Button>
      </form>
    </Card>
  );
};
