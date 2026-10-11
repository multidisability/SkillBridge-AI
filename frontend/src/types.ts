export type SkillStatus = 'supported' | 'not_evidenced'

export interface RequirementResult {
  requirement_id: string
  skill: string
  job_quote: string
  status: SkillStatus
  profile_quote: string | null
  reason: string
}

export interface LearningDay {
  day: number
  focus: string
  action: string
  deliverable: string
}

export interface AnalyzeResponse {
  requirements: RequirementResult[]
  coverage: { supported: number; total: number }
  learning_plan: LearningDay[]
  notice: string
}
