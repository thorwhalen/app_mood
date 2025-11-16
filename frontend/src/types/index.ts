export interface Mood {
  id: string;
  name: string;
  description: string;
  attribute_definition: string;
  user_id?: string;
  created_at: string;
  updated_at: string;
}

export interface MoodCreate {
  name: string;
  description: string;
  attribute_definition: string;
}

export interface Dataset {
  id: string;
  mood_id: string;
  num_examples: number;
  openai_model_used?: string;
  status: 'pending' | 'generating' | 'completed' | 'failed';
  error_message?: string;
  generated_at: string;
  examples?: DatasetExample[];
}

export interface DatasetExample {
  id: string;
  text: string;
  score: number;
  created_at: string;
}

export interface DatasetCreate {
  num_examples: number;
  openai_model: string;
}

export interface MLModel {
  id: string;
  mood_id: string;
  model_type: 'numerical_regression' | 'binary_classification' | 'ordinal_regression';
  metrics?: Record<string, number>;
  is_selected: boolean;
  trained_at: string;
}

export interface Analysis {
  id: string;
  mood_id: string;
  model_id?: string;
  user_id?: string;
  input_text: string;
  score: number;
  analyzed_at: string;
}

export interface AnalysisCreate {
  mood_id: string;
  text: string;
}

export interface HeadlineAnalysis {
  headline: string;
  sentiment_score: number;
  source?: string;
}

export interface Task {
  id: string;
  task_type: 'generate_dataset' | 'train_model' | 'batch_analysis';
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  result?: any;
  error?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}
