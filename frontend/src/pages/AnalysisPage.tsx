import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import {
  Box,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  LinearProgress,
} from '@mui/material'
import { moodsApi, analysisApi } from '@/services/api'
import type { AnalysisCreate } from '@/types'

export default function AnalysisPage() {
  const [moodId, setMoodId] = useState('')
  const [text, setText] = useState('')
  const [result, setResult] = useState<number | null>(null)

  const { data: moods, isLoading } = useQuery({
    queryKey: ['moods'],
    queryFn: () => moodsApi.list().then((res) => res.data),
  })

  const analysisMutation = useMutation({
    mutationFn: (data: AnalysisCreate) => analysisApi.analyze(data),
    onSuccess: (response) => {
      setResult(response.data.score)
    },
  })

  const handleAnalyze = () => {
    if (!moodId || !text) return
    setResult(null)
    analysisMutation.mutate({ mood_id: moodId, text })
  }

  const getScoreColor = (score: number) => {
    if (score < 0.3) return 'error'
    if (score < 0.7) return 'warning'
    return 'success'
  }

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Text Analysis
      </Typography>
      <Typography variant="body1" paragraph>
        Analyze sentiment in text using trained mood models.
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Select Mood</InputLabel>
            <Select
              value={moodId}
              label="Select Mood"
              onChange={(e) => setMoodId(e.target.value)}
            >
              {moods?.map((mood) => (
                <MenuItem key={mood.id} value={mood.id}>
                  {mood.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            label="Text to Analyze"
            multiline
            rows={6}
            fullWidth
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter financial text to analyze..."
            sx={{ mb: 2 }}
          />

          <Button
            variant="contained"
            onClick={handleAnalyze}
            disabled={!moodId || !text || analysisMutation.isPending}
            fullWidth
          >
            {analysisMutation.isPending ? 'Analyzing...' : 'Analyze'}
          </Button>
        </CardContent>
      </Card>

      {analysisMutation.isError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Analysis failed. Make sure the mood has a trained and selected model.
        </Alert>
      )}

      {result !== null && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Analysis Result
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="h3" color={`${getScoreColor(result)}.main`}>
                {result.toFixed(3)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Score (0 = negative, 1 = positive)
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={result * 100}
              color={getScoreColor(result)}
              sx={{ height: 10, borderRadius: 5 }}
            />
          </CardContent>
        </Card>
      )}
    </Box>
  )
}
