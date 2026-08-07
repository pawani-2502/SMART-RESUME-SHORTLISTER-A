import sampleJob from "../../sample-data/sample-job.json";
import sampleJobs from "../../sample-data/sample-jobs.json";
import sampleResumes from "../../sample-data/sample-resumes.json";
import sampleRankings from "../../sample-data/sample-rankings.json";
import sampleInterviews from "../../sample-data/sample-interviews.json";
import sampleAnalytics from "../../sample-data/sample-analytics.json";
import sampleReports from "../../sample-data/sample-reports.json";
import sampleScreening from "../../sample-data/sample-screening.json";
import sampleInterviewPacks from "../../sample-data/sample-interview-packs.json";

export const demoData = {
  job: sampleJob,
  jobs: sampleJobs.jobs,
  resumes: sampleResumes,
  rankings: sampleRankings,
  interview: sampleInterviews,
  analytics: sampleAnalytics,
  reports: sampleReports,
  screening: sampleScreening,
  interviewPacks: sampleInterviewPacks,
} as const;

export type DemoData = typeof demoData;
